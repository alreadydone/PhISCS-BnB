import numpy as np

I_small = np.array(
    [[1, 0],
     [0, 1],
     [1, 1]]
)

I0 = np.array(
    [[0, 1, 0],
     [0, 0, 1],
     [1, 0, 1],
     [0, 1, 0],
     [0, 1, 0],
     [1, 1, 0]
     ])




I1 = np.array([[0, 1, 1, 0], [1, 0, 0, 1], [1, 1, 0, 0], [0, 0, 1, 0]])

I2 = np.array([[0, 1, 1, 0], [1, 1, 0, 1], [1, 1, 0, 0], [0, 1, 1, 0]])

I3 = np.array([[0, 1, 1, 0, 1], [1, 0, 0, 1, 1], [1, 1, 0, 0, 0], [0, 0, 1, 0, 0]])

I5 = np.array([[0, 1, 1, 0], [1, 0, 0, 1], [1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]])

I6 = np.array(
    [
        [1, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 1, 0, 1],
        [1, 1, 0, 1, 1, 1, 1, 0],
        [1, 0, 0, 0, 0, 1, 1, 0],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [1, 1, 1, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 1, 0, 1],
        [0, 1, 1, 0, 1, 0, 1, 1],
    ]
)

instances = [I0, I1, I2, I3, I5, I6]


def getRandomMatrix(n, m):
    return np.random.randint(2, size=(n, m))


if __name__ == "__main__":
    print(getRandomMatrix(5, 5))
