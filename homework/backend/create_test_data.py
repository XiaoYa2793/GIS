from app import app, db, HistoricalMap
import os

# 测试数据
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

# 在应用上下文中添加数据
with app.app_context():
    # 检查是否已有数据
    existing_map = HistoricalMap.query.first()
    if existing_map:
        print(f"数据库中已存在历史地图数据，共有{HistoricalMap.query.count()}条记录")
    else:
        # 添加数据
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
        
        # 提交事务
        db.session.commit()
        print(f"成功添加{len(maps_data)}条历史地图数据") 