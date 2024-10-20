# Initialize the frontend
cd rivol_imt
npm install
cd ..

# Create the databases
python booking/database/database.py
python movie/database/database.py
python showtime/database/database.py
python user/database/database.py

# Compile gRPC proto files
cd booking
python -m grpc_tools.protoc -I=./protos --python_out=. --grpc_python_out=. booking.proto
python -m grpc_tools.protoc -I=./protos --python_out=. --grpc_python_out=. showtime.proto
cd ..
cd showtime
python -m grpc_tools.protoc -I=./protos --python_out=. --grpc_python_out=. showtime.proto
cd ..
cd user
python -m grpc_tools.protoc -I=./protos --python_out=. --grpc_python_out=. booking.proto
python -m grpc_tools.protoc -I=./protos --python_out=. --grpc_python_out=. showtime.proto
cd ..
