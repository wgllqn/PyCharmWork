from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging
import os
import uuid
import json
from typing import Dict, Any, Optional

from app.config import settings, get_database_url
from app.models import (
    FileUploadResponse, QueryRequest, QueryResponse,
    VisualizationRequest, VisualizationResponse,
    ChatRequest, ChatResponse, ChatMessage
)
from app.sql_agent import SQLAgentManager
from app.visualization import DataVisualizer
from utils.file_processor import FileProcessor
from app.database import DatabaseManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 尝试导入 data_manager
DATA_MANAGER_AVAILABLE = False
data_manager = None
try:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from data_manager import data_manager as dm
    data_manager = dm
    DATA_MANAGER_AVAILABLE = True
    logger.info("Data manager loaded successfully")
except Exception as e:
    logger.warning(f"Data manager not available: {e}")

# 全局存储
file_store: Dict[str, Dict] = {}
chat_sessions: Dict[str, Dict] = {}
sql_agents: Dict[str, SQLAgentManager] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 创建必要的目录
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/visualizations", exist_ok=True)
    logger.info("Application startup complete")
    yield
    # 清理资源
    for agent in sql_agents.values():
        agent.cleanup()
    logger.info("Application shutdown complete")


# 创建FastAPI应用
app = FastAPI(
    title="SQL Agent API",
    description="基于LangChain的SQL数据分析API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 路由定义
@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径，返回简单的API文档"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SQL Agent API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .endpoint { margin: 20px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
            code { background: #e8e8e8; padding: 2px 5px; }
        </style>
    </head>
    <body>
        <h1>SQL Agent API</h1>
        <p>基于LangChain的SQL数据分析服务</p>

        <h2>API端点</h2>

        <div class="endpoint">
            <h3>POST /upload</h3>
            <p>上传CSV或Excel文件</p>
            <code>Content-Type: multipart/form-data</code>
        </div>

        <div class="endpoint">
            <h3>POST /query</h3>
            <p>使用自然语言查询数据</p>
            <code>Content-Type: application/json</code>
        </div>

        <div class="endpoint">
            <h3>POST /visualize</h3>
            <p>创建数据可视化图表</p>
            <code>Content-Type: application/json</code>
        </div>

        <div class="endpoint">
            <h3>POST /chat</h3>
            <p>与数据对话分析</p>
            <code>Content-Type: application/json</code>
        </div>

        <p><a href="/docs">查看完整API文档</a></p>
    </body>
    </html>
    """


@app.get("/datasources")
async def get_data_sources():
    """获取所有数据源（数据库表 + 上传的文件）"""
    sources = []

    # 获取外部数据库表
    try:
        db_manager_instance = DatabaseManager()
        if db_manager_instance.connect():
            tables = db_manager_instance.get_tables()
            logger.info(f"✅ 从外部数据库获取到 {len(tables)} 个表")

            for table_name in tables:
                info = db_manager_instance.get_table_info(table_name)
                if info:
                    sources.append({
                        "name": table_name,
                        "table": table_name,
                        "rows": info.get("row_count", 0),
                        "columns": [col["name"] for col in info.get("columns", [])],
                        "description": f"数据库表 ({db_manager_instance.db_type})",
                        "source": "database"  # 标记为真实数据库来源
                    })

            db_manager_instance.close()
        else:
            logger.warning("外部数据库连接失败，尝试使用 data_manager")
            # 如果外部数据库连接失败，回退到 data_manager
            if DATA_MANAGER_AVAILABLE and data_manager:
                try:
                    db_tables = data_manager.get_table_list()
                    sources.extend(db_tables)
                except Exception as e:
                    logger.error(f"Error getting database tables from data_manager: {e}")
    except Exception as e:
        logger.error(f"Error connecting to external database: {e}")
        # 回退到 data_manager
        if DATA_MANAGER_AVAILABLE and data_manager:
            try:
                db_tables = data_manager.get_table_list()
                sources.extend(db_tables)
            except Exception as e2:
                logger.error(f"Error getting database tables: {e2}")

    # 添加上传的文件
    for file_id, file_info in file_store.items():
        sources.append({
            "name": file_info["filename"],
            "table": f"file_{file_id}",
            "rows": file_info.get("estimated_rows", 0),
            "columns": file_info.get("headers", []),
            "description": "用户上传的文件",
            "source": "upload",
            "file_id": file_id
        })

    logger.info(f"📊 总共返回 {len(sources)} 个数据源")

    return {
        "success": True,
        "sources": sources
    }


@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    上传并处理CSV或Excel文件
    """
    try:
        # 检查文件类型
        file_type = file.filename.split('.')[-1].lower()
        if file_type not in ['csv', 'xlsx', 'xls']:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # 读取文件内容
        content = await file.read()
        file_type_str = 'csv' if file_type == 'csv' else 'excel'

        # 处理文件
        result = FileProcessor.get_file_headers(content, file_type_str)

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])

        # 生成文件ID并存储
        file_id = str(uuid.uuid4())
        file_store[file_id] = {
            "filename": file.filename,
            "content": content,
            "file_type": file_type_str,
            "headers": result["headers"],
            "column_info": result["column_info"]
        }

        logger.info(f"File uploaded successfully: {file.filename} (ID: {file_id})")

        return FileUploadResponse(
            success=True,
            file_id=file_id,
            message=f"File '{file.filename}' uploaded successfully",
            headers=result["headers"],
            column_info=result["column_info"],
            total_columns=result["total_columns"],
            estimated_rows=result["estimated_rows"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_data(request: QueryRequest):
    """
    使用自然语言查询数据（支持文件上传和数据库表）
    """
    try:
        agent_key = None
        
        # 优先使用 file_id（CSV上传文件）
        if request.file_id and request.file_id in file_store:
            agent_key = f"file_{request.file_id}"
            file_info = file_store[request.file_id]
            
            logger.info(f"[CSV查询] 处理上传文件: {file_info.get('filename', 'unknown')}")
            logger.info(f"[CSV查询] 用户问题: {request.query}")

            # 获取或创建SQL Agent
            if agent_key not in sql_agents:
                logger.info(f"[CSV查询] 创建新的SQL Agent for {agent_key}")
                agent = SQLAgentManager(
                    openai_api_key=settings.openai_api_key,
                    openai_base_url=settings.openai_base_url,
                    model=settings.default_model
                )

                # 创建数据库（使用更有意义的表名）
                table_name = f"file_{request.file_id}"
                db_result = agent.create_database_from_file(
                    file_info["content"],
                    file_info["file_type"],
                    table_name=table_name
                )

                if not db_result["success"]:
                    raise HTTPException(status_code=500, detail=db_result["error"])

                # 创建SQL Agent
                agent_result = agent.create_sql_agent()

                if not agent_result["success"]:
                    raise HTTPException(status_code=500, detail=agent_result["error"])

                sql_agents[agent_key] = agent
            else:
                logger.info(f"[CSV查询] 重用已有的SQL Agent for {agent_key}")

        # 使用 table_name（从数据库）
        elif request.table_name:
            agent_key = f"table_{request.table_name}"

            # 获取或创建SQL Agent
            if agent_key not in sql_agents:
                agent = SQLAgentManager(
                    openai_api_key=settings.openai_api_key,
                    openai_base_url=settings.openai_base_url,
                    model=settings.default_model
                )

                # 优先使用外部数据库配置
                db_url = get_database_url()
                logger.info(f"Connecting to database: {db_url.split('@')[-1] if '@' in db_url else db_url}")

                # 如果是 SQLite，检查文件是否存在
                if db_url.startswith("sqlite"):
                    db_path = db_url.replace("sqlite:///", "")
                    if not os.path.exists(db_path):
                        # 尝试使用 data_manager
                        if DATA_MANAGER_AVAILABLE and data_manager:
                            logger.info(f"Using data_manager for table: {request.table_name}")
                            db_path = data_manager.db_path if hasattr(data_manager, 'db_path') else None
                            if db_path and os.path.exists(db_path):
                                db_url = f"sqlite:///{db_path}"
                            else:
                                raise HTTPException(status_code=404, detail="Database file not found. Please initialize the database first.")
                        else:
                            raise HTTPException(status_code=404, detail="Database file not found")

                # 连接到数据库
                from langchain_community.utilities import SQLDatabase
                try:
                    agent.db = SQLDatabase.from_uri(db_url)
                    logger.info(f"✅ Successfully connected to database")
                except Exception as e:
                    logger.error(f"❌ Failed to connect to database: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

                # 创建SQL Agent
                agent_result = agent.create_sql_agent()
                if not agent_result["success"]:
                    raise HTTPException(status_code=500, detail=agent_result["error"])

                sql_agents[agent_key] = agent
                logger.info(f"Created SQL Agent for table: {request.table_name}")
        
        else:
            raise HTTPException(status_code=400, detail="Either file_id or table_name must be provided")

        agent = sql_agents[agent_key]

        # 执行查询
        is_csv_query = agent_key.startswith("file_")
        if is_csv_query:
            logger.info(f"[CSV查询] 开始执行查询...")
        logger.info(f"Executing query: {request.query} on {agent_key}")
        
        result = agent.query_data(request.query)

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])

        # 获取查询结果
        data = result.get("data", [])
        columns = result.get("columns", [])
        sql = result.get("sql")
        answer = result.get("answer", "")
        reasoning = result.get("reasoning", [])
        
        if is_csv_query:
            logger.info(f"[CSV查询] 查询完成: SQL={sql[:50] if sql else None}..., 数据行数={len(data)}, 答案长度={len(answer) if answer else 0}")
        
        logger.info(f"Query result: data rows={len(data)}, columns={len(columns)}, has_sql={bool(sql)}, has_answer={bool(answer)}")
        if answer:
            logger.info(f"Answer preview: {answer[:200]}...")
        
        # 如果有 SQL 但没有数据，尝试执行 SQL 获取数据
        if sql and not data:
            try:
                logger.info(f"Executing SQL to get data: {sql[:100]}...")
                sql_result = agent.execute_custom_sql(sql)
                if sql_result["success"]:
                    data = sql_result["data"]
                    columns = sql_result["columns"]
                    logger.info(f"SQL execution successful: {len(data)} rows retrieved")
            except Exception as e:
                logger.warning(f"Could not execute SQL to get data: {e}")
                import traceback
                traceback.print_exc()

        # 确保数据格式正确
        if data and not columns:
            columns = list(data[0].keys()) if data else []
        
        # 不要在后端再次截断数据，使用 SQL 中的 LIMIT
        final_data = data
        
        return QueryResponse(
            success=True,
            answer=answer,
            sql=sql,
            reasoning=reasoning,
            data=final_data,
            returned_rows=len(final_data),
            columns=columns,
            total_rows=len(final_data)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/visualize", response_model=VisualizationResponse)
async def create_visualization(request: VisualizationRequest):
    """
    创建数据可视化图表
    """
    try:
        # 检查文件ID
        if not request.file_id or request.file_id not in file_store:
            raise HTTPException(status_code=404, detail="File not found")

        file_info = file_store[request.file_id]

        # 获取数据
        data_result = FileProcessor.query_data(
            file_info["content"],
            file_info["file_type"],
            "查询所有数据",
            limit=request.limit
        )

        if not data_result["success"]:
            raise HTTPException(status_code=500, detail=data_result["error"])

        # 创建可视化
        viz_result = DataVisualizer.create_chart(
            data_result["data"],
            request.chart_type,
            request.x_column,
            request.y_column,
            request.group_by,
            request.title
        )

        if not viz_result["success"]:
            raise HTTPException(status_code=500, detail=viz_result["error"])

        return VisualizationResponse(
            success=True,
            chart_html=viz_result["chart_html"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat_with_data(request: ChatRequest):
    """
    与数据进行对话分析
    """
    try:
        # 生成或获取会话ID
        session_id = request.session_id or str(uuid.uuid4())

        # 初始化会话
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                "messages": [],
                "file_id": request.file_id
            }

        session = chat_sessions[session_id]

        # 添加用户消息
        user_message = ChatMessage(role="user", content=request.message)
        session["messages"].append(user_message)

        # 获取文件信息
        file_id = request.file_id or session.get("file_id")
        if not file_id or file_id not in file_store:
            raise HTTPException(status_code=404, detail="No file associated with chat")

        file_info = file_store[file_id]

        # 获取或创建SQL Agent
        if file_id not in sql_agents:
            agent = SQLAgentManager(
                openai_api_key=settings.openai_api_key,
                openai_base_url=settings.openai_base_url,
                model=settings.default_model
            )

            # 创建数据库
            db_result = agent.create_database_from_file(
                file_info["content"],
                file_info["file_type"]
            )

            if not db_result["success"]:
                raise HTTPException(status_code=500, detail=db_result["error"])

            # 创建SQL Agent
            agent_result = agent.create_sql_agent()

            if not agent_result["success"]:
                raise HTTPException(status_code=500, detail=agent_result["error"])

            sql_agents[file_id] = agent

        agent = sql_agents[file_id]

        # 执行查询
        result = agent.query_data(request.message)

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])

        # 添加助手回复
        assistant_message = ChatMessage(role="assistant", content=result["answer"])
        session["messages"].append(assistant_message)

        return ChatResponse(
            success=True,
            message=result["answer"],
            session_id=session_id,
            data=result.get("data")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
async def list_files():
    """列出所有上传的文件"""
    files = []
    for file_id, info in file_store.items():
        files.append({
            "file_id": file_id,
            "filename": info["filename"],
            "file_type": info["file_type"],
            "total_columns": len(info["headers"]),
            "estimated_rows": info.get("estimated_rows")
        })
    return {"files": files}


@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """删除文件"""
    if file_id not in file_store:
        raise HTTPException(status_code=404, detail="File not found")

    # 清理SQL Agent
    if file_id in sql_agents:
        sql_agents[file_id].cleanup()
        del sql_agents[file_id]

    # 删除文件
    del file_store[file_id]

    return {"success": True, "message": "File deleted successfully"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "files_loaded": len(file_store),
        "active_agents": len(sql_agents),
        "active_sessions": len(chat_sessions)
    }


@app.get("/database/info")
async def get_database_info():
    """获取数据库连接信息和表列表"""
    try:
        db_manager = DatabaseManager()
        if not db_manager.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to database")

        tables = db_manager.get_tables()
        table_details = []

        # 获取每个表的详细信息
        for table_name in tables:
            info = db_manager.get_table_info(table_name)
            if info:
                table_details.append({
                    "name": table_name,
                    "rows": info.get("row_count", 0),
                    "columns": [col["name"] for col in info.get("columns", [])],
                    "column_count": info.get("column_count", 0)
                })

        db_manager.close()

        return {
            "success": True,
            "db_type": db_manager.db_type,
            "db_url": db_manager._mask_password(db_manager.db_url),
            "tables": table_details,
            "table_count": len(tables)
        }

    except Exception as e:
        logger.error(f"Error getting database info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/database/test")
async def test_database_connection():
    """测试数据库连接"""
    try:
        db_manager = DatabaseManager()
        result = db_manager.test_connection()
        db_manager.close()

        if result["success"]:
            return {
                "success": True,
                "message": "✅ Database connection successful!",
                "db_type": result["db_type"],
                "db_url": result["db_url"],
                "tables": result["tables"],
                "table_count": result["table_count"]
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Connection failed"))

    except Exception as e:
        logger.error(f"Error testing database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )