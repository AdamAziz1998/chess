Command to preprocessdata
python neuralNetwork/preprocess/csv_to_memmap.py --csv assets/data/dataset.csv --out_dir neuralNetwork/processed --moves_col -2 --workers 16


Command to train neural network
python neuralNetwork/train.py --meta neuralNetwork/processed/meta.json --epochs 20 --batch_size 512 --lr 0.001

Command to create the chess DB
python chessDatabase/dataTransform.py --csv assets/data/dataset.csv 


In development:
Command to preprocessdata
python neuralNetwork/preprocess/csv_to_memmap.py --csv assets/data/dataset.csv --out_dir neuralNetwork/processed --moves_col -2 --workers 16 --rows_limit 10

Command to train neural network
python neuralNetwork/train.py --meta neuralNetwork/processed/meta.json --epochs 2 --batch_size 512 --lr 0.001

Command to create the chess DB
python chessDatabase/dataTransform.py --csv assets/data/dataset.csv 
(inside the file uncomment the row limiter)