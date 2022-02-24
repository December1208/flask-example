from flask_migrate import Migrate, MigrateCommand
from flask_script import Server, Manager

from app import app
from app.extensions import db
from app.settings import setting
from sqlalchemy_utils import database_exists, create_database, drop_database

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server('0.0.0.0', port=8000))


@manager.command
def create_db():
    if setting.TESTING:
        with app.app_context():
            engine_url = db.engine.url
            if not database_exists(engine_url):
                print(f'开始创建数据库: {engine_url}')
                create_database(engine_url)
            else:
                drop_database(engine_url)
                print(f'数据库已存在，重新创建: {engine_url}')
                create_database(engine_url)
            db.create_all()
    else:
        print(f'没事别搁这乱创建数据库哟！')


@manager.command
def drop_db():
    if setting.TESTING:
        with app.app_context():
            engine_url = db.engine.url
            if database_exists(engine_url):
                db.drop_all()
                drop_database(engine_url)
                print(f'删除数据库成功: {engine_url}')
    else:
        print(f'您这是准备跑路了？')


if __name__ == "__main__":
    manager.run()
