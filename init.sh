# Initialize the frontend
cd rivol_imt
npm install
cd ..

# Create the databases
python booking/database/database.py
python movie/database/database.py
python showtime/database/database.py
python user/database/database.py
