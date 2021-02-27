from app import app
from werkzeug.security import generate_password_hash

if __name__ == '__main__':
    app.run(debug=False, host='10.128.0.2', port=443, threaded=True, ssl_context=("/etc/letsencrypt/live/yakuhai.com/fullchain.pem","/etc/letsencrypt/live/yakuhai.com/privkey.pem"))
    #app.run(debug=False, host='127.0.0.1', port=80, threaded=True)

