from app import create_app

webapp = create_app()
if __name__ == '__main__':
    webapp.run(host='0.0.0.0', port=8080, debug=True)
