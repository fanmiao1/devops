from app import app
import sys

reload(sys)

sys.setdefaultencoding('utf-8')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090,debug=True)
