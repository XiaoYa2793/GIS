from flask import Flask, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
import logging
import json
import requests
import datetime
import math
import flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 配置JWT
app.config['JWT_SECRET_KEY'] = 'beijing-travel-jwt-secret-key'  # 更改为复杂的密钥
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)
jwt = JWTManager(app)

# 配置数据库
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'beijing_travel.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 在app.py中添加存储路径常量
RECOMMENDATION_DATA_DIR = os.path.join(basedir, 'data', 'recommendations')

# 确保数据目录存在
os.makedirs(RECOMMENDATION_DATA_DIR, exist_ok=True)

# 添加一个测试路由
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Backend is running!"})

# 景点模型
class Attraction(db.Model):
    __tablename__ = 'attraction'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    coordinates = db.Column(db.String(50))
    category = db.Column(db.String(50))
    image_path = db.Column(db.String(500))

# 历史地图模型
class HistoricalMap(db.Model):
    __tablename__ = 'historical_map'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    period = db.Column(db.String(50), nullable=False)
    year_range = db.Column(db.String(50), nullable=False)
    year = db.Column(db.String(20))  # 年份简写
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    center_coordinate = db.Column(db.String(50), default='116.397428,39.90923')  # 地图中心坐标
    zoom_level = db.Column(db.Integer, default=12)  # 默认缩放级别
    overlay_bounds = db.Column(db.String(100))  # 地图覆盖范围
    additional_info = db.Column(db.Text)  # 额外信息

# 历史地图兴趣点模型
class MapPoint(db.Model):
    __tablename__ = 'map_point'
    id = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.Integer, db.ForeignKey('historical_map.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    point_type = db.Column(db.String(50))  # 地点类型：古迹、宫殿、城门等
    coordinates = db.Column(db.String(50), nullable=False)  # 经纬度坐标
    icon_path = db.Column(db.String(500))  # 图标路径
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

# 用户模型
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 推荐景点模型
class Recommendation(db.Model):
    __tablename__ = 'recommendation'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    attractions = db.Column(db.Text, nullable=False)  # 存储景点ID，以逗号分隔

# API路由
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working!"})

@app.route('/api/attractions', methods=['GET'])
def get_attractions():
    try:
        logger.info("正在获取景点数据...")
        attractions = Attraction.query.all()
        logger.info(f"成功获取到 {len(attractions)} 个景点")
        
        # 检查数据是否为空
        if not attractions:
            logger.warning("数据库中没有景点数据")
            return jsonify([])
            
        # 转换数据并验证
        result = []
        for a in attractions:
            data = {
                'id': a.id,
                'name': a.name,
                'description': a.description,
                'location': a.location,
                'coordinates': a.coordinates,
                'category': a.category,
                'image_path': a.image_path
            }
            # 验证必要字段
            if not all(key in data for key in ['id', 'name', 'image_path']):
                logger.error(f"景点数据缺少必要字段: {data}")
                continue
            result.append(data)
            
        logger.info(f"返回 {len(result)} 个有效景点数据")
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取景点数据时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/init-data', methods=['GET', 'POST'])
def init_data():
    try:
        logger.info("正在检查数据库是否已初始化...")
        # 检查是否已有数据
        existing_data = Attraction.query.first()
        if existing_data is not None:
            logger.info("数据库已经包含数据，跳过初始化")
            return jsonify({
                'message': '数据已存在',
                'data': {
                    'name': existing_data.name,
                    'total': Attraction.query.count()
                }
            })
        
        logger.info("开始初始化数据...")
        
        # 从 SQL 文件读取数据
        sql_file_path = os.path.join(basedir, 'sql', 'attraction.sql')
        logger.info(f"读取 SQL 文件: {sql_file_path}")
        
        if not os.path.exists(sql_file_path):
            logger.error(f"SQL 文件不存在: {sql_file_path}")
            return jsonify({'error': 'SQL 文件不存在'}), 404
            
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_data = f.read()
            
        if not sql_data.strip():
            logger.error("SQL 文件为空")
            return jsonify({'error': 'SQL 文件为空'}), 400
        
        # 分割并执行每条 SQL 语句
        sql_statements = [stmt.strip() for stmt in sql_data.split(';') if stmt.strip()]
        logger.info(f"找到 {len(sql_statements)} 条 SQL 语句")
        
        for statement in sql_statements:
            try:
                db.session.execute(text(statement))
                logger.debug(f"成功执行 SQL: {statement[:100]}...")
            except Exception as e:
                logger.error(f"执行 SQL 语句时出错: {str(e)}\nSQL: {statement}")
                raise e
        
        db.session.commit()
        
        # 验证数据是否成功插入
        total_attractions = Attraction.query.count()
        logger.info(f"数据初始化成功，共插入 {total_attractions} 条记录")
        return jsonify({
            'message': '数据初始化成功',
            'data': {
                'total': total_attractions
            }
        })
    except Exception as e:
        logger.error(f"初始化数据时出错: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 添加静态文件服务
@app.route('/images/<path:filename>')
def serve_image(filename):
    logger.info(f"请求图片: {filename}")
    try:
        return send_from_directory('static/images', filename)
    except Exception as e:
        logger.error(f"加载图片失败 {filename}: {str(e)}")
        return jsonify({'error': '图片不存在'}), 404

@app.route('/api/proxy/panorama')
def proxy_panorama():
    try:
        # 转发请求到故宫全景网站
        response = requests.get('https://pano.dpm.org.cn/gugong')
        
        # 设置必要的响应头
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': response.headers.get('Content-Type', 'text/html')
        }
        
        return response.content, response.status_code, headers
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/redirect/gugong-panorama', methods=['GET'])
def gugong_panorama_redirect():
    try:
        logger.info("请求故宫全景重定向")
        
        # 这里可以使用实际的接口获取URL，现在直接返回固定URL
        panorama_url = 'https://www.720yun.com/vr/bc021cO6uu6'
        
        return jsonify({
            'status': 'success',
            'redirect_url': panorama_url,
            'message': '获取故宫全景URL成功'
        })
    except Exception as e:
        logger.error(f"获取故宫全景URL出错: {str(e)}")
        return jsonify({'status': 'error', 'message': f'获取故宫全景URL出错: {str(e)}'}), 500

@app.route('/api/redirect/yiheyuan-panorama')
def redirect_yiheyuan_panorama():
    """重定向到颐和园全景网站"""
    try:
        # 这里可以添加记录访问日志的逻辑
        logger.info("用户请求访问颐和园全景")
        
        # 返回重定向URL而不是直接重定向，让前端处理跳转
        return jsonify({
            'status': 'success',
            'redirect_url': 'https://www.720yun.com/vr/b542cabuaba'
        })
    except Exception as e:
        logger.error(f"重定向到颐和园全景时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '重定向失败'
        }), 500

@app.route('/api/redirect/tiantan-panorama')
def redirect_tiantan_panorama():
    """重定向到天坛全景网站"""
    try:
        # 这里可以添加记录访问日志的逻辑
        logger.info("用户请求访问天坛全景")
        
        # 返回重定向URL而不是直接重定向，让前端处理跳转
        return jsonify({
            'status': 'success',
            'redirect_url': 'https://www.720yun.com/t/12vkuyies7q?scene_id=39471371'
        })
    except Exception as e:
        logger.error(f"重定向到天坛全景时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '重定向失败'
        }), 500

@app.route('/api/redirect/changcheng-panorama')
def redirect_changcheng_panorama():
    """重定向到长城全景网站"""
    try:
        # 这里可以添加记录访问日志的逻辑
        logger.info("用户请求访问长城全景")
        
        # 返回重定向URL而不是直接重定向，让前端处理跳转
        return jsonify({
            'status': 'success',
            'redirect_url': 'https://www.720yun.com/t/ce0jtswwsm2?scene_id=14052175'
        })
    except Exception as e:
        logger.error(f"重定向到长城全景时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '重定向失败'
        }), 500

# 历史地图API
@app.route('/api/historical-maps', methods=['GET'])
def get_historical_maps():
    try:
        maps = HistoricalMap.query.all()
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': m.id,
                    'name': m.name,
                    'period': m.period,
                    'year_range': m.year_range,
                    'year': m.year,
                    'description': m.description,
                    'image_path': m.image_path,
                    'center_coordinate': m.center_coordinate,
                    'zoom_level': m.zoom_level,
                    'overlay_bounds': m.overlay_bounds,
                    'additional_info': m.additional_info
                } for m in maps
            ]
        })
    except Exception as e:
        logger.error(f"获取历史地图数据时出错: {str(e)}")
        return jsonify({'status': 'error', 'message': f'获取历史地图数据时出错: {str(e)}'}), 500

# 获取特定时期的数据
@app.route('/api/periods', methods=['GET'])
def get_periods():
    try:
        logger.info("正在获取时期数据...")
        
        # 获取地图时期
        map_periods = db.session.query(HistoricalMap.period).distinct().all()
        map_periods = [p[0] for p in map_periods]
        
        # 合并去重
        all_periods = sorted(list(set(map_periods)))
        
        logger.info(f"成功获取到 {len(all_periods)} 个时期")
        return jsonify(all_periods)
    except Exception as e:
        logger.error(f"获取时期数据时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 初始化历史地图数据
@app.route('/api/init-historical-maps', methods=['GET'])
def init_historical_maps():
    try:
        # 检查是否已有数据
        existing_data = HistoricalMap.query.first()
        if existing_data:
            logger.info(f"历史地图数据已存在，共有{HistoricalMap.query.count()}条记录")
            return jsonify({
                'status': 'success',
                'message': f'历史地图数据已存在，共有{HistoricalMap.query.count()}条记录'
            })
        
        # 添加历史地图数据
        maps_data = [
            {
                'name': '元大都城垣图',
                'period': '元代',
                'year_range': '1271年至1368年',
                'year': '1271',
                'description': '元大都是元朝的首都，今北京城的前身。元大都城垣呈方形，城周长约28.6千米，面积约50平方千米，为中国古代城市之最。',
                'image_path': '/images/maps/yuan_dadu.jpg',
                'center_coordinate': '116.397428,39.90923',
                'zoom_level': 12,
                'overlay_bounds': '116.324867,39.954929,116.469877,39.864929',
                'additional_info': '元大都规划井然有序，城池气势宏伟，是13世纪世界上最大最先进的城市之一。'
            },
            {
                'name': '明北京城图',
                'period': '明代',
                'year_range': '1368年至1644年',
                'year': '1420',
                'description': '明代北京城由内城和外城组成，内城又称"内皇城"，为皇帝及宫廷人员居住地，外城又称"外城区"，为平民区。',
                'image_path': '/images/maps/ming_beijing.jpg',
                'center_coordinate': '116.397428,39.90923',
                'zoom_level': 13,
                'overlay_bounds': '116.324867,39.954929,116.469877,39.864929',
                'additional_info': '明代北京城形成了目前北京旧城的基本格局，特别是城市中轴线的规划，影响至今。'
            },
            {
                'name': '清北京城全图',
                'period': '清代',
                'year_range': '1644年至1912年',
                'year': '1750',
                'description': '清代北京城在明代基础上进一步完善，内城为满族人居住，外城为汉族人居住，城内设有八旗驻防。',
                'image_path': '/images/maps/qing_beijing.jpg',
                'center_coordinate': '116.397428,39.90923',
                'zoom_level': 13,
                'overlay_bounds': '116.324867,39.954929,116.469877,39.864929',
                'additional_info': '清代北京城发展到鼎盛时期，城市规模扩大，建筑精美，文化繁荣。'
            },
            {
                'name': '民国北平城市图',
                'period': '民国',
                'year_range': '1912年至1949年',
                'year': '1935',
                'description': '民国时期的北平（今北京）逐渐从传统城市向现代城市转型，城市功能分区开始出现，但仍保留了大量的历史古迹。',
                'image_path': '/images/maps/minguo_beiping.jpg',
                'center_coordinate': '116.397428,39.90923',
                'zoom_level': 13,
                'overlay_bounds': '116.324867,39.954929,116.469877,39.864929',
                'additional_info': '民国时期北平城墙拆除部分，建设了一些现代设施，城市开始向现代化转型。'
            },
            {
                'name': '现代北京城市规划图',
                'period': '当代',
                'year_range': '1949年至今',
                'year': '2010',
                'description': '现代北京城为中华人民共和国首都，是国家的政治、文化中心，已发展成为国际化大都市，但仍保留着丰富的历史文化遗产。',
                'image_path': '/images/maps/modern_beijing.jpg',
                'center_coordinate': '116.397428,39.90923',
                'zoom_level': 11,
                'overlay_bounds': '116.224867,40.054929,116.569877,39.764929',
                'additional_info': '现代北京已形成环形+放射状的城市空间格局，既有现代化城区，又保留了历史文化街区。'
            }
        ]
        
        for data in maps_data:
            historical_map = HistoricalMap(
                name=data['name'],
                period=data['period'],
                year_range=data['year_range'],
                year=data['year'],
                description=data['description'],
                image_path=data['image_path'],
                center_coordinate=data['center_coordinate'],
                zoom_level=data['zoom_level'],
                overlay_bounds=data['overlay_bounds'],
                additional_info=data['additional_info']
            )
            db.session.add(historical_map)
        
        db.session.commit()
        logger.info(f"成功添加{len(maps_data)}条历史地图数据")
        
        return jsonify({
            'status': 'success',
            'message': f'成功添加{len(maps_data)}条历史地图数据'
        })
    except Exception as e:
        logger.error(f"初始化历史地图数据出错: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'初始化历史地图数据出错: {str(e)}'
        }), 500

# 获取特定地图的兴趣点
@app.route('/api/historical-maps/<int:map_id>/points', methods=['GET'])
def get_map_points(map_id):
    try:
        logger.info(f"获取地图ID={map_id}的兴趣点")
        points = MapPoint.query.filter_by(map_id=map_id).all()
        
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': p.id,
                    'map_id': p.map_id,
                    'name': p.name,
                    'description': p.description,
                    'point_type': p.point_type,
                    'coordinates': p.coordinates,
                    'icon_path': p.icon_path
                } for p in points
            ]
        })
    except Exception as e:
        logger.error(f"获取地图兴趣点出错: {str(e)}")
        return jsonify({'status': 'error', 'message': f'获取地图兴趣点出错: {str(e)}'}), 500

# 初始化历史地图兴趣点数据
@app.route('/api/init-map-points', methods=['GET'])
def init_map_points():
    try:
        # 检查是否已有数据
        existing_points = MapPoint.query.first()
        if existing_points:
            logger.info(f"地图兴趣点数据已存在，共有{MapPoint.query.count()}条记录")
            return jsonify({
                'status': 'success',
                'message': f'地图兴趣点数据已存在，共有{MapPoint.query.count()}条记录'
            })
        
        # 获取已有的地图数据
        maps = HistoricalMap.query.all()
        if not maps:
            logger.error("未找到历史地图数据，请先初始化历史地图")
            return jsonify({
                'status': 'error',
                'message': '未找到历史地图数据，请先初始化历史地图'
            }), 400
        
        # 创建地图ID到ID的映射
        map_name_to_id = {m.name: m.id for m in maps}
        
        # 添加兴趣点数据
        points_data = [
            # 元代地图兴趣点
            {
                'map_name': '元大都城垣图',
                'name': '大都宫城',
                'description': '元大都的宫城，位于今北京故宫一带。',
                'point_type': '宫殿',
                'coordinates': '116.397428,39.91923',
                'icon_path': '/images/icons/palace.png'
            },
            {
                'map_name': '元大都城垣图',
                'name': '大都城墙',
                'description': '元大都的城墙，比明清北京城墙范围更大。',
                'point_type': '城墙',
                'coordinates': '116.387428,39.95923',
                'icon_path': '/images/icons/wall.png'
            },
            
            # 明代地图兴趣点
            {
                'map_name': '明北京城图',
                'name': '紫禁城',
                'description': '明朝皇宫，即今日故宫。',
                'point_type': '宫殿',
                'coordinates': '116.397428,39.91923',
                'icon_path': '/images/icons/palace.png'
            },
            {
                'map_name': '明北京城图',
                'name': '天坛',
                'description': '明朝皇帝祭天的场所。',
                'point_type': '祭祀',
                'coordinates': '116.407526,39.882206',
                'icon_path': '/images/icons/temple.png'
            },
            {
                'map_name': '明北京城图',
                'name': '前门',
                'description': '北京内城的南门，又称正阳门。',
                'point_type': '城门',
                'coordinates': '116.397230,39.900517',
                'icon_path': '/images/icons/gate.png'
            },
            
            # 清代地图兴趣点
            {
                'map_name': '清北京城全图',
                'name': '颐和园',
                'description': '清代皇家园林，原名清漪园。',
                'point_type': '园林',
                'coordinates': '116.275147,39.999183',
                'icon_path': '/images/icons/garden.png'
            },
            {
                'map_name': '清北京城全图',
                'name': '圆明园',
                'description': '清代皇家园林，被誉为"万园之园"。',
                'point_type': '园林',
                'coordinates': '116.298864,40.007414',
                'icon_path': '/images/icons/garden.png'
            },
            {
                'map_name': '清北京城全图',
                'name': '景山',
                'description': '位于紫禁城北面的人工山，是俯瞰北京城的最佳地点。',
                'point_type': '景观',
                'coordinates': '116.397425,39.928258',
                'icon_path': '/images/icons/scenery.png'
            },
            
            # 民国地图兴趣点
            {
                'map_name': '民国北平城市图',
                'name': '北京大学',
                'description': '民国时期重要的教育机构，当时位于今什刹海附近。',
                'point_type': '教育',
                'coordinates': '116.383196,39.941621',
                'icon_path': '/images/icons/education.png'
            },
            {
                'map_name': '民国北平城市图',
                'name': '北海公园',
                'description': '始建于辽代的皇家园林，民国时期对外开放。',
                'point_type': '园林',
                'coordinates': '116.382202,39.926238',
                'icon_path': '/images/icons/garden.png'
            },
            
            # 现代地图兴趣点
            {
                'map_name': '现代北京城市规划图',
                'name': '国家大剧院',
                'description': '位于人民大会堂西侧，是现代北京的文化地标。',
                'point_type': '文化',
                'coordinates': '116.383751,39.903607',
                'icon_path': '/images/icons/culture.png'
            },
            {
                'map_name': '现代北京城市规划图',
                'name': '鸟巢',
                'description': '2008年北京奥运会主场馆，现代北京的象征之一。',
                'point_type': '体育',
                'coordinates': '116.396791,39.992908',
                'icon_path': '/images/icons/sports.png'
            },
            {
                'map_name': '现代北京城市规划图',
                'name': '中央电视台总部大楼',
                'description': '中央电视台总部，现代北京的建筑地标。',
                'point_type': '媒体',
                'coordinates': '116.477362,39.915062',
                'icon_path': '/images/icons/media.png'
            }
        ]
        
        for data in points_data:
            # 通过地图名称查找地图ID
            map_id = map_name_to_id.get(data['map_name'])
            if not map_id:
                logger.warning(f"未找到地图: {data['map_name']}")
                continue
                
            point = MapPoint(
                map_id=map_id,
                name=data['name'],
                description=data['description'],
                point_type=data['point_type'],
                coordinates=data['coordinates'],
                icon_path=data['icon_path']
            )
            db.session.add(point)
        
        db.session.commit()
        logger.info(f"成功添加{len(points_data)}个地图兴趣点")
        
        return jsonify({
            'status': 'success',
            'message': f'成功添加{len(points_data)}个地图兴趣点'
        })
    except Exception as e:
        logger.error(f"初始化地图兴趣点数据出错: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'初始化地图兴趣点数据出错: {str(e)}'
        }), 500

@app.route('/api/check-map-config', methods=['GET'])
def check_map_config():
    logger.info("检查地图配置")
    try:
        return jsonify({
            'status': 'success',
            'message': '地图配置检查API可以访问',
            'debug': {
                'static_folder': app.static_folder,
                'basedir': basedir,
                'image_path': os.path.join(basedir, 'static', 'images', 'maps')
            }
        })
    except Exception as e:
        logger.error(f"检查地图配置出错: {str(e)}")
        return jsonify({'status': 'error', 'message': f'检查地图配置出错: {str(e)}'}), 500

# 设置CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    # 添加额外的CORS头以允许打开外部链接
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/api/recommendations', methods=['POST'])
def create_recommendation():
    try:
        data = request.json
        logger.info(f"创建景点推荐: {data}")
        
        if not data or 'title' not in data or 'attractions' not in data:
            return jsonify({'error': '缺少必要参数'}), 400
            
        # 验证景点ID是否存在
        attraction_ids = data['attractions']
        if not isinstance(attraction_ids, list) or len(attraction_ids) == 0:
            return jsonify({'error': '景点列表格式不正确'}), 400
            
        for attraction_id in attraction_ids:
            attraction = Attraction.query.get(attraction_id)
            if not attraction:
                return jsonify({'error': f'景点 ID {attraction_id} 不存在'}), 404
        
        # 创建推荐记录
        recommendation = Recommendation(
            title=data['title'],
            description=data.get('description', ''),
            attractions=','.join(map(str, attraction_ids))
        )
        
        db.session.add(recommendation)
        db.session.commit()
        
        # 查询景点详细信息
        attractions = Attraction.query.filter(Attraction.id.in_(attraction_ids)).all()
        attractions_data = []
        for attraction in attractions:
            attractions_data.append({
                'id': attraction.id,
                'name': attraction.name,
                'description': attraction.description,
                'location': attraction.location,
                'coordinates': attraction.coordinates,
                'category': attraction.category,
                'image_path': attraction.image_path
            })
            
        # 构建完整推荐数据
        recommendation_data = {
            'id': recommendation.id,
            'title': recommendation.title,
            'description': recommendation.description,
            'created_at': recommendation.created_at.isoformat(),
            'attractions': attractions_data
        }
        
        # 保存到JSON文件
        json_file_path = os.path.join(RECOMMENDATION_DATA_DIR, f'{recommendation.id}.json')
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(recommendation_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"推荐数据已保存到: {json_file_path}")
        
        return jsonify(recommendation_data), 201
    except Exception as e:
        logger.error(f"创建景点推荐时出错: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/<int:recommendation_id>', methods=['GET'])
def get_recommendation(recommendation_id):
    try:
        # 先尝试从JSON文件中读取
        json_file_path = os.path.join(RECOMMENDATION_DATA_DIR, f'{recommendation_id}.json')
        if os.path.exists(json_file_path):
            logger.info(f"从JSON文件加载推荐: {json_file_path}")
            with open(json_file_path, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        
        # 如果文件不存在，从数据库读取并创建文件
        logger.info(f"从数据库加载推荐: {recommendation_id}")
        recommendation = Recommendation.query.get(recommendation_id)
        if not recommendation:
            return jsonify({'error': '推荐不存在'}), 404
            
        attraction_ids = list(map(int, recommendation.attractions.split(',')))
        attractions = Attraction.query.filter(Attraction.id.in_(attraction_ids)).all()
        
        attractions_data = []
        for attraction in attractions:
            attractions_data.append({
                'id': attraction.id,
                'name': attraction.name,
                'description': attraction.description,
                'location': attraction.location,
                'coordinates': attraction.coordinates,
                'category': attraction.category,
                'image_path': attraction.image_path
            })
        
        recommendation_data = {
            'id': recommendation.id,
            'title': recommendation.title,
            'description': recommendation.description,
            'created_at': recommendation.created_at.isoformat(),
            'attractions': attractions_data
        }
        
        # 保存到JSON文件(延迟创建)
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(recommendation_data, f, ensure_ascii=False, indent=2)
            
        return jsonify(recommendation_data)
    except Exception as e:
        logger.error(f"获取景点推荐时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 修改HTML模板为更友好的展示方式，避免直接显示JSON格式
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>北京旅游 - {{ title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 100%;
            margin: 0 auto;
            padding: 0;
        }
        
        .header {
            background: linear-gradient(135deg, #42b983, #2c3e50);
            color: white;
            padding: 20px 15px;
            text-align: center;
            margin-bottom: 20px;
            position: relative;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            margin: 0;
            font-size: 1.8rem;
            font-weight: 700;
        }
        
        .header p {
            margin: 5px 0 0;
            opacity: 0.9;
            font-size: 1rem;
        }
        
        .content {
            padding: 0 15px 20px;
        }
        
        .description {
            background-color: rgba(66, 185, 131, 0.1);
            border-left: 4px solid #42b983;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 0 5px 5px 0;
            font-size: 0.95rem;
        }
        
        .section-title {
            font-size: 1.3rem;
            color: #2c3e50;
            margin: 25px 0 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #eee;
        }
        
        .attraction-card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.08);
            margin-bottom: 25px;
            overflow: hidden;
        }
        
        .attraction-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }
        
        .attraction-content {
            padding: 15px;
        }
        
        .attraction-title {
            margin-top: 0;
            margin-bottom: 10px;
            color: #2c3e50;
            font-size: 1.4rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .category-badge {
            background-color: #42b983;
            color: white;
            font-size: 0.75rem;
            padding: 3px 8px;
            border-radius: 20px;
            font-weight: normal;
            margin-left: 8px;
        }
        
        .location {
            color: #666;
            font-size: 0.9rem;
            margin: 10px 0;
            display: flex;
            align-items: center;
        }
        
        .location-icon {
            margin-right: 5px;
            color: #42b983;
        }
        
        .coordinates {
            color: #888;
            font-size: 0.8rem;
            margin-top: 5px;
            font-family: monospace;
        }
        
        .attraction-description {
            font-size: 0.95rem;
            line-height: 1.6;
            margin: 12px 0;
            color: #444;
        }
        
        .button-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        
        .button {
            background-color: #42b983;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            flex: 1;
            min-width: 120px;
            justify-content: center;
            box-shadow: 0 2px 5px rgba(66, 185, 131, 0.3);
        }
        
        .button:hover {
            background-color: #3aa876;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(66, 185, 131, 0.4);
        }
        
        .button-icon {
            margin-right: 6px;
            font-size: 1.1rem;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px 15px;
            color: #777;
            font-size: 0.85rem;
            background: #f1f1f1;
            border-top: 1px solid #e5e5e5;
        }
        
        .footer p {
            margin: 5px 0;
        }
        
        .footer a {
            color: #42b983;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        /* 美化文字显示 */
        .text-highlight {
            background-color: rgba(66, 185, 131, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        /* 响应式调整 */
        @media (min-width: 768px) {
            .container {
                max-width: 700px;
                padding: 20px;
            }
            .header {
                border-radius: 12px;
                margin-bottom: 25px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
            <p>北京旅游景点推荐</p>
        </div>
        
        <div class="content">
            {% if description and description != "好" %}
            <div class="description">
                <p>{{ description }}</p>
            </div>
            {% endif %}
            
            <h2 class="section-title">推荐景点：</h2>
            
            {% for attraction in attractions %}
            <div class="attraction-card">
                {% if attraction.image_path %}
                <img class="attraction-image" src="{{ server_url }}{{ attraction.image_path }}" alt="{{ attraction.name }}" onerror="this.src='https://via.placeholder.com/800x400?text=北京旅游景点'">
                {% endif %}
                
                <div class="attraction-content">
                    <h3 class="attraction-title">
                        {{ attraction.name }}
                        {% if attraction.category %}
                        <span class="category-badge">{{ attraction.category }}</span>
                        {% endif %}
                    </h3>
                    
                    {% if attraction.location %}
                    <div class="location">
                        <span class="location-icon">📍</span> {{ attraction.location }}
                    </div>
                    {% endif %}
                    
                    {% if attraction.coordinates %}
                    <div class="coordinates">GPS: {{ attraction.coordinates }}</div>
                    {% endif %}
                    
                    <p class="attraction-description">{{ attraction.description }}</p>
                    
                    <div class="button-container">
                        {% if attraction.coordinates %}
                        <a href="https://api.map.baidu.com/marker?location={{ attraction.coordinates.split(',')[1] }},{{ attraction.coordinates.split(',')[0] }}&title={{ attraction.name }}&content={{ attraction.name }}&output=html" class="button" target="_blank">
                            <span class="button-icon">🗺️</span> 地图导航
                        </a>
                        {% endif %}
                        
                        <a href="{{ server_url }}/attraction/{{ attraction.id }}" class="button">
                            <span class="button-icon">ℹ️</span> 详细信息
                        </a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>创建于 {{ created_at }}</p>
            <p>访问时间: {{ current_time }}</p>
            <p>
                <a href="{{ server_url }}/recommendation/{{ id }}?format=json" target="_blank">查看JSON数据</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

# 修改二维码重定向函数，支持HTML显示
@app.route('/recommendation/<int:recommendation_id>', methods=['GET'])
def recommendation_redirect(recommendation_id):
    """
    处理二维码扫描后的重定向，将用户导向前端页面或直接显示数据
    """
    logger.info(f"接收到推荐ID重定向请求: {recommendation_id}")
    
    # 获取请求参数
    accept_header = request.headers.get('Accept', '')
    format_param = request.args.get('format')
    is_api_request = 'application/json' in accept_header and 'text/html' not in accept_header
    is_mobile = 'mobile' in request.headers.get('User-Agent', '').lower()
    
    # 验证推荐是否存在并获取数据
    json_file_path = os.path.join(RECOMMENDATION_DATA_DIR, f'{recommendation_id}.json')
    recommendation_data = None
    
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            recommendation_data = json.load(f)
    else:
        # 从数据库获取
        try:
            recommendation = Recommendation.query.get(recommendation_id)
            if not recommendation:
                return jsonify({'error': '推荐不存在'}), 404
                
            attraction_ids = list(map(int, recommendation.attractions.split(',')))
            attractions = Attraction.query.filter(Attraction.id.in_(attraction_ids)).all()
            
            attractions_data = []
            for attraction in attractions:
                attractions_data.append({
                    'id': attraction.id,
                    'name': attraction.name,
                    'description': attraction.description,
                    'location': attraction.location,
                    'coordinates': attraction.coordinates,
                    'category': attraction.category,
                    'image_path': attraction.image_path
                })
            
            recommendation_data = {
                'id': recommendation.id,
                'title': recommendation.title,
                'description': recommendation.description,
                'created_at': recommendation.created_at.isoformat(),
                'attractions': attractions_data
            }
            
            # 保存到JSON文件
            os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(recommendation_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"获取推荐数据出错: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # 如果是API请求或明确要求JSON格式，返回JSON数据
    if is_api_request or format_param == 'json':
        return jsonify(recommendation_data)
    
    # 如果是移动设备或要求HTML格式，直接显示HTML页面
    if is_mobile or format_param == 'html' or request.args.get('direct') == 'true':
        # 添加服务器URL和当前时间
        recommendation_data['server_url'] = request.host_url.rstrip('/')
        recommendation_data['current_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 渲染HTML模板
        return render_template_string(HTML_TEMPLATE, **recommendation_data)
    
    # 否则重定向到前端页面
    frontend_base_url = request.host_url.rstrip('/')
    
    # 特殊处理本地开发环境
    if frontend_base_url.startswith('http://localhost:5000'):
        frontend_base_url = 'http://localhost:8080'
    
    frontend_url = f"{frontend_base_url}/recommendation/{recommendation_id}"
    logger.info(f"重定向到前端URL: {frontend_url}")
    
    return flask.redirect(frontend_url, code=302)

# 修复attraction_redirect函数，提供HTML显示功能
@app.route('/attraction/<int:attraction_id>', methods=['GET'])
def attraction_redirect(attraction_id):
    """
    处理景点二维码扫描后的重定向，将用户导向前端页面或直接显示数据
    """
    logger.info(f"接收到景点ID重定向请求: {attraction_id}")
    
    # 获取请求参数
    accept_header = request.headers.get('Accept', '')
    format_param = request.args.get('format')
    is_api_request = 'application/json' in accept_header and 'text/html' not in accept_header
    is_mobile = 'mobile' in request.headers.get('User-Agent', '').lower()
    
    # 验证景点是否存在
    attraction = Attraction.query.get(attraction_id)
    if not attraction:
        return jsonify({'error': '景点不存在'}), 404
    
    # API请求或明确要求JSON格式时，直接返回数据
    if is_api_request or format_param == 'json':
        return jsonify({
            'id': attraction.id,
            'name': attraction.name,
            'description': attraction.description,
            'location': attraction.location,
            'coordinates': attraction.coordinates,
            'category': attraction.category,
            'image_path': attraction.image_path
        })
    
    # 如果是移动设备或要求HTML格式，直接显示HTML页面
    if is_mobile or format_param == 'html' or request.args.get('direct') == 'true':
        # 准备数据
        attraction_data = {
            'id': attraction.id,
            'title': attraction.name,
            'description': attraction.description,
            'attractions': [{
                'id': attraction.id,
                'name': attraction.name,
                'description': attraction.description,
                'location': attraction.location,
                'coordinates': attraction.coordinates,
                'category': attraction.category,
                'image_path': attraction.image_path
            }],
            'server_url': request.host_url.rstrip('/'),
            'current_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'created_at': '当前查看'
        }
        
        # 渲染HTML模板
        return render_template_string(HTML_TEMPLATE, **attraction_data)
    
    # 否则重定向到前端页面
    frontend_base_url = request.host_url.rstrip('/')
    
    # 特殊处理本地开发环境
    if frontend_base_url.startswith('http://localhost:5000'):
        frontend_base_url = 'http://localhost:8080'
    
    frontend_url = f"{frontend_base_url}/attraction/{attraction_id}"
    logger.info(f"重定向到前端URL: {frontend_url}")
    
    return flask.redirect(frontend_url, code=302)

# 视频文件API
@app.route('/api/videos', methods=['GET'])
def get_videos():
    try:
        video_dir = os.path.join(basedir, 'frontend', 'static', 'mv展示')
        if not os.path.exists(video_dir):
            return jsonify({
                'status': 'error',
                'message': '视频目录不存在'
            }), 404
            
        video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]
        video_files.sort()  # 按文件名排序
        
        video_data = []
        for idx, file in enumerate(video_files):
            # 提取时期信息 - 根据视频顺序与历史地图对应
            period = ''
            if idx == 0:
                period = '元代'
            elif idx == 1:
                period = '明代'
            elif idx == 2:
                period = '清代'
            elif idx == 3:
                period = '民国'
            elif idx == 4:
                period = '当代'
            else:
                period = f'扩展时期 {idx+1}'
                
            video_data.append({
                'id': idx + 1,
                'filename': file,
                'url': f'/videos/{file}',
                'period': period,
                'year': f'{1200 + idx * 150}',  # 简单估算年份
                'name': f'北京{period}影像'
            })
            
        return jsonify({
            'status': 'success',
            'data': video_data
        })
    except Exception as e:
        logger.error(f"获取视频列表时出错: {str(e)}")
        return jsonify({'status': 'error', 'message': f'获取视频列表时出错: {str(e)}'}), 500

# 提供视频文件服务
@app.route('/videos/<path:filename>')
def serve_video(filename):
    logger.info(f"请求视频: {filename}")
    try:
        response = send_from_directory('../frontend/static/mv展示', filename)
        # 添加CORS头，允许跨域访问
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        logger.error(f"加载视频失败 {filename}: {str(e)}")
        return jsonify({'error': '视频不存在'}), 404

# ///////////////////////////////////////////////////////////////////////////////
# 百度地图 API 配置
BAIDU_SERVER_AK = 'mvULQ1iMcjGZLjpEOSPKfRUdMRuvIwV1'  # 替换为你的百度地图开发者 AK

# 地理编码函数
def geocode(address):
    params = {
        'ak': BAIDU_SERVER_AK,
        'address': address,
        'output': 'json',
        'ret_coordtype': 'bd09ll'
    }
    try:
        response = requests.get('https://api.map.baidu.com/geocoding/v3/', 
                             params=params,
                             timeout=10)
        data = response.json()
        
        if data.get('status') == 0:
            if not data.get('result') or not data['result'].get('location'):
                print(f"地理编码警告: {address} - 返回结果不完整")
                return None
            return data['result']['location']
            
        print(f"地理编码警告: {address} - {data.get('message', '未知错误')}")
        return None
        
    except Exception as e:
        print(f"地理编码异常: {address} - {str(e)}")
        return None

def parse_path_points(path_str):
    result = []
    for point in path_str.split(';'):
        try:
            lng, lat = map(float, point.split(','))
            result.append([lat, lng])
        except ValueError:
            continue
    return result


@app.route('/api/navigation-by-place', methods=['GET'])
def navigation_by_place():
    start = request.args.get('start')
    end = request.args.get('end')
    mode = request.args.get('mode', 'driving')  # 默认驾车

    if not start or not start.strip() or not end or not end.strip():
        return jsonify({
            "status": 400,
            "message": "起点和终点参数不能为空或空白"
        }), 400

    try:
        start_coord = geocode(start)
        if not start_coord:
            return jsonify({
                "status": 404,
                "message": f"无法获取起点'{start}'的坐标，请检查地名是否正确"
            }), 404

        end_coord = geocode(end)
        if not end_coord:
            return jsonify({
                "status": 404,
                "message": f"无法获取终点'{end}'的坐标，请检查地名是否正确"
            }), 404

    except requests.exceptions.Timeout:
        return jsonify({"status": 504, "message": "地理编码服务响应超时，请稍后重试"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"status": 500, "message": f"网络请求错误: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"status": 500, "message": f"服务器内部错误: {str(e)}"}), 500

    api_endpoints = {
        'driving': 'https://api.map.baidu.com/directionlite/v1/driving',
        'transit': 'https://api.map.baidu.com/directionlite/v1/transit',
        'riding': 'https://api.map.baidu.com/directionlite/v1/riding',
        'walking': 'https://api.map.baidu.com/directionlite/v1/walking'
    }

    if mode not in api_endpoints:
        return jsonify({"status": 400, "message": "不支持的交通方式"}), 400

    # 策略定义
    tactics_map = {
        'driving': [
            ("默认路线", "0"),
            ("时间优先", "1"),
            ("距离最短", "2"),
            ("避开高速", "3"),
            ("高速优先", "4"),
            ("躲避拥堵", "5"),
        ],
        'transit': [
            ("默认路线", "0"),
            ("地铁优先", "3"),
            ("最少换乘", "5"),
            ("最少步行", "10")
        ],
        'riding': [
            ("默认路线", None)
        ],
        'walking': [
            ("默认路线", None)
        ]
    }

    route_list = []

    try:
        for tactic_label, tactic_code in tactics_map[mode]:
            params = {
                "ak": BAIDU_SERVER_AK,
                "origin": f"{start_coord['lat']},{start_coord['lng']}",
                "destination": f"{end_coord['lat']},{end_coord['lng']}",
                "coord_type": "bd09ll"
            }

            if tactic_code is not None:
                params["tactics"] = tactic_code

            if mode == 'transit':
                params["transit_mode"] = "subway|bus"

            response = requests.get(api_endpoints[mode], params=params, timeout=15)
            data = response.json()

            if data.get('status') != 0:
                continue

            routes = data.get('result', {}).get('routes', [])
            if not routes:
                continue

            for route in routes:
                route_points = []
                transit_details = []

                if mode in ['driving', 'walking', 'riding']:
                    for step in route.get('steps', []):
                        if step.get('path'):
                            route_points += parse_path_points(step['path'])

                elif mode == 'transit':
                    for segment in route.get('steps', []):
                        for step in segment:
                            if isinstance(step, dict):
                                if 'path' in step:
                                    route_points += parse_path_points(step['path'])

                                if 'vehicle' in step:
                                    vehicle = step['vehicle']
                                    transit_details.append({
                                        'type': vehicle.get('type', 'unknown'),
                                        'line_name': vehicle.get('name', ''),
                                        'start_station': step.get('start_location', {}).get('name', ''),
                                        'end_station': step.get('end_location', {}).get('name', ''),
                                        'duration': step.get('duration', 0),
                                        'distance': step.get('distance', 0),
                                        'path': step.get('path', '')
                                    })
                                elif step.get('type') == 5:  # 步行
                                    transit_details.append({
                                        'type': 'WALKING',
                                        'line_name': '',
                                        'start_station': '',
                                        'end_station': '',
                                        'duration': step.get('duration', 0),
                                        'distance': step.get('distance', 0),
                                        'path': step.get('path', '')
                                    })

                # 去重路径点
                unique_points = []
                seen = set()
                for point in route_points:
                    pt_tuple = tuple(point)
                    if pt_tuple not in seen:
                        seen.add(pt_tuple)
                        unique_points.append(point)

                route_obj = {
                    "points": unique_points if unique_points else [
                        [start_coord['lat'], start_coord['lng']],
                        [end_coord['lat'], end_coord['lng']]
                    ],
                    "distance": route.get('distance'),
                    "duration": route.get('duration'),
                    "tactic": tactic_label,
                    "transit_details": transit_details if mode == 'transit' else None
                }

                route_list.append(route_obj)

        if not route_list:
            return jsonify({"status": 404, "message": "未找到有效的路线"}), 404

        return jsonify({
            "status": 0,
            "routes": route_list,
            "mode": mode
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"请求百度地图API时出错: {str(e)}")
        # 创建简单路线
        try:
            route_obj = create_simple_route(float(current_lat), float(current_lng), dest_coord, destination, start_name)
            return jsonify({
                "status": 0,
                "route": route_obj,
                "mode": mode,
                "note": "使用简单路线代替，因为导航API请求失败"
            })
        except Exception as inner_e:
            logger.error(f"创建简单路线时出错: {str(inner_e)}")
            return jsonify({"status": 503, "message": "地图服务暂时不可用，请稍后再试"}), 503
    except Exception as e:
        logger.error(f"获取导航路线时发生错误: {str(e)}")
        try:
            route_obj = create_simple_route(float(current_lat), float(current_lng), dest_coord, destination, start_name)
            return jsonify({
                "status": 0,
                "route": route_obj,
                "mode": mode,
                "note": "使用简单路线代替，因为发生了错误"
            })
        except Exception as inner_e:
            logger.error(f"创建简单路线时出错: {str(inner_e)}")
            return jsonify({"status": 500, "message": f"服务器错误: {str(e)}"}), 500

# 创建简单的直线路线
def create_simple_route(current_lat, current_lng, dest_coord, destination_name, start_name="当前位置", mode="walking"):
    distance = calculate_distance(current_lat, current_lng, dest_coord['lat'], dest_coord['lng'])
    
    # 根据不同交通方式设置不同的速度
    # 步行: 5km/h, 骑行: 15km/h, 驾车: 60km/h
    if mode == "walking":
        estimated_speed = 5000  # 步行速度 5km/h (m/h)
    elif mode == "riding" or mode == "cycling":
        estimated_speed = 15000  # 骑行速度 15km/h (m/h)
    elif mode == "driving":
        estimated_speed = 60000  # 驾车速度 60km/h (m/h)
    else:
        estimated_speed = 5000  # 默认步行速度
    
    # 对于超长距离的特殊处理
    if distance > 100000 and mode == "driving":  # 大于100公里可能是高速或飞机
        estimated_speed = 100000  # 高速 100km/h (m/h)
            
    # 计算预计时间（秒）
    duration = int((distance / estimated_speed) * 3600)
    
    # 格式化距离显示
    distance_text = ""
    if distance >= 1000:
        distance_text = f"{distance/1000:.1f}公里"
    else:
        distance_text = f"{int(distance)}米"
    
    # 格式化时间显示
    duration_text = ""
    if duration >= 3600:
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        duration_text = f"{hours}小时{minutes}分钟"
    else:
        minutes = duration // 60
        if minutes == 0:
            duration_text = "1分钟"  # 最少显示1分钟
        else:
            duration_text = f"{minutes}分钟"
    
    return {
        "points": [
            [current_lat, current_lng],
            [dest_coord['lat'], dest_coord['lng']]
        ],
        "distance": distance,
        "distance_text": distance_text,
        "duration": duration,
        "duration_text": duration_text,
        "navigation_steps": [
            {
                'instruction': f"从{start_name}出发，前往{destination_name}",
                'distance': distance,
                'duration': duration,
                'path': f"{current_lng},{current_lat};{dest_coord['lng']},{dest_coord['lat']}"
            }
        ],
        "current_location": [current_lat, current_lng],
        "destination": [dest_coord['lat'], dest_coord['lng']]
    }

# 计算两点之间的距离（米）
def calculate_distance(lat1, lng1, lat2, lng2):
    # 地球半径（米）
    R = 6371000
    # 将经纬度转换为弧度
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # 经纬度差
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    # 使用Haversine公式计算
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2) * math.sin(dlng/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

# 添加获取当前位置的API
@app.route('/api/current-location', methods=['GET'])
def get_current_location():
    try:
        # 此处为示例，实际应从前端获取
        current_location = {
            'lat': 39.9097,
            'lng': 116.3976,
            'address': '北京市'
        }
        return jsonify(current_location)
    except Exception as e:
        logger.error(f"获取当前位置时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 用户注册API
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # 验证必要字段
        if not all(key in data for key in ['username', 'email', 'password']):
            return jsonify({'error': '缺少必要信息'}), 400
            
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '用户名已存在'}), 409
            
        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '邮箱已存在'}), 409
            
        # 创建新用户
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        # 返回用户信息和token
        access_token = create_access_token(identity=new_user.id)
        
        return jsonify({
            'message': '注册成功',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email
            },
            'access_token': access_token
        }), 201
    except Exception as e:
        logger.error(f"用户注册时出错: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 用户登录API
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # 验证必要字段
        if not all(key in data for key in ['username', 'password']):
            return jsonify({'error': '缺少用户名或密码'}), 400
            
        # 查找用户
        user = User.query.filter_by(username=data['username']).first()
        
        # 验证用户和密码
        if not user or not user.check_password(data['password']):
            return jsonify({'error': '用户名或密码错误'}), 401
            
        # 更新最后登录时间
        user.last_login = datetime.datetime.now()
        db.session.commit()
        
        # 创建token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': '登录成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'access_token': access_token
        })
    except Exception as e:
        logger.error(f"用户登录时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 获取当前用户信息API
@app.route('/api/auth/user', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        # 从token获取用户ID
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
            
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        })
    except Exception as e:
        logger.error(f"获取用户信息时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 添加地理编码API接口
@app.route('/api/geocode', methods=['GET'])
def geocode_api():
    try:
        address = request.args.get('address')
        if not address:
            return jsonify({
                'status': -1,
                'message': '缺少地址参数'
            }), 400
        
        # 调用百度地图API进行地理编码
        location = geocode(address)
        if not location:
            return jsonify({
                'status': -1,
                'message': f'无法获取地址"{address}"的坐标'
            }), 404
        
        return jsonify({
            'status': 0,
            'message': '成功',
            'location': location,
            'address': address
        })
    except Exception as e:
        logger.error(f"地理编码API出错: {str(e)}")
        return jsonify({
            'status': -1,
            'message': f'地理编码错误: {str(e)}'
        }), 500

# 添加真实导航API端点
@app.route('/api/real-navigation', methods=['GET'])
def real_navigation():
    try:
        # 获取请求参数
        current_lat = request.args.get('current_lat', type=float)
        current_lng = request.args.get('current_lng', type=float)
        destination = request.args.get('destination')
        mode = request.args.get('mode', 'walking')
        start_name = request.args.get('start_name', '当前位置')
        allow_foreign = request.args.get('allow_foreign', 'false').lower() == 'true'
        
        logger.info(f"Real Navigation 请求: 从 [{current_lat},{current_lng}] 到 {destination}, 模式: {mode}")
        
        if not current_lat or not current_lng or not destination:
            logger.error("缺少必要参数")
            return jsonify({
                'status': -1,
                'message': '缺少必要参数'
            })
        
        # 验证坐标是否在合理范围内（除非明确允许国外坐标）
        if not allow_foreign and not (29 <= current_lat <= 45 and 110 <= current_lng <= 125):
            logger.warning(f"坐标 [{current_lat},{current_lng}] 不在中国大陆范围内，但继续处理")
            # 不再强制替换为默认坐标
        
        # 对目的地进行地理编码，获取坐标
        dest_coord = geocode(destination)
        if not dest_coord:
            logger.error(f"无法获取目的地 '{destination}' 的坐标")
            # 创建默认坐标（故宫）作为备用
            dest_coord = {'lat': 39.916345, 'lng': 116.397155}
        
        # 这里复用已有的路径规划功能，调用create_simple_route函数，并传入交通方式模式
        route = create_simple_route(current_lat, current_lng, dest_coord, destination, start_name, mode)
        
        return jsonify({
            'status': 0,
            'message': '成功',
            'route': route
        })
        
    except Exception as e:
        logger.error(f"实时导航出错: {str(e)}")
        return jsonify({
            'status': -1,
            'message': f'导航出错: {str(e)}'
        }), 500

if __name__ == '__main__':
    db_path = os.path.join(basedir, 'beijing_travel.db')
    
    # 只在数据库文件不存在时创建数据库
    if not os.path.exists(db_path):
        logger.info("数据库文件不存在，正在创建...")
        with app.app_context():
            try:
                db.create_all()
                logger.info("数据库表创建成功")
            except Exception as e:
                logger.error(f"创建数据库表时出错: {str(e)}")
    else:
        logger.info("数据库文件已存在，跳过创建步骤")
    
    # 创建默认用户
    with app.app_context():
        try:
            # 检查默认用户是否已存在
            default_user = User.query.filter_by(username='admin').first()
            if not default_user:
                # 创建默认用户
                default_user = User(
                    username='admin',
                    email='admin@example.com'
                )
                default_user.set_password('123456')
                
                # 添加到数据库
                db.session.add(default_user)
                db.session.commit()
                logger.info("默认用户'admin'创建成功，密码为'123456'")
            else:
                logger.info("默认用户'admin'已存在，跳过创建步骤")
        except Exception as e:
            logger.error(f"创建默认用户时出错: {str(e)}")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 