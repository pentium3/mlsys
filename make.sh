cd proto
rm *.py
rm -rf __pycache__
python3 -m grpc_tools.protoc -I. --python_out=./ --grpc_python_out=./ ./data.proto
cd ..
