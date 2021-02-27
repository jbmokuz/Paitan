rm ~/mahjong.db

rm -rf ./migrations 


flask db init
flask db migrate -m "Inital migration"
flask db upgrade
