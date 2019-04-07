cd proto
del *.py
rmdir /s /q __pycache__
python -m grpc_tools.protoc -I. --python_out=./ --grpc_python_out=./ ./data.proto