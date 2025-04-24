# Tworzymy katalog proto, jeśli jeszcze nie istnieje
New-Item -ItemType Directory -Force -Path ./proto

# Uruchamiamy polecenie protoc z poetry
poetry run python -m grpc_tools.protoc `
  -I ../proto `
  --python_out=./proto `
  --pyi_out=./proto `
  --grpc_python_out=./proto `
  ../proto/*.proto
