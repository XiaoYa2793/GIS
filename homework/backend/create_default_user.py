from app import app, db, User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_default_user():
    with app.app_context():
        # 检查默认用户是否已存在
        default_user = User.query.filter_by(username='admin').first()
        if default_user:
            logger.info("默认用户'admin'已存在，无需创建")
            return

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

if __name__ == '__main__':
    try:
        create_default_user()
        logger.info("脚本执行完成")
    except Exception as e:
        logger.error(f"创建默认用户时出错: {str(e)}") 