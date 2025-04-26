
from app import app

# This allows running both locally and in production
if __name__ == '__main__':
    # Use 0.0.0.0 to make it externally visible
    app.run(host='0.0.0.0', port=5000)
