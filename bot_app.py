from config import Config
from app import fapp


if __name__ == '__main__':
    fapp.run(debug=True, host=Config.APP_URL)
