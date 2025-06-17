
```bash
Before concat:
y_train        X_train
--------       ----------------------
[0, 1, 0]       [[5.1, 3.5], [6.2, 2.8], [5.9, 3.0]]


After concat:

train_data:
incident | feature1 | feature2
-------- | -------- | --------
   0     |   5.1    |   3.5
   1     |   6.2    |   2.8
   0     |   5.9    |   3.0
```   