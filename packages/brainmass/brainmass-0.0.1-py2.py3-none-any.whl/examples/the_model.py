# Copyright 2025 BDP Ecosystem Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


import time  # for timer

import matplotlib.pyplot as plt  # for plotting
import numpy as np  # for numerical operations

from rww_pytorch_model import Model_fitting, ParamsJR, RNNWWD

start_time = time.time()

from datasets import Dataset

hcp = Dataset('hcp')

sc = hcp.Cmat
sc = sc - np.diag(np.diag(sc))
sc = 0.5 * (sc.T + sc)
sc = np.log1p(sc) / np.linalg.norm(np.log1p(sc))

dist = np.nan_to_num(1 / sc)
dist[dist > 200] = 0

ts = np.mean(np.asarray(hcp.BOLDs), axis=0)
ts = ts / np.max(ts)
# ts = np.ones((100, 83))
fc_emp = np.corrcoef(ts)

node_size = sc.shape[0]
output_size = sc.shape[0]
num_epoches = 20
batch_size = 20
step_size = .05
input_size = 2
tr = .75

## call WWD module
par = ParamsJR(
    "WWD",
    g=[80, .2],
    g_EE=[0.5, 5],
    g_IE=[0.5, 5],
    g_EI=[0.16963709468378746, 10],
    I_0=[0.39410256410256406, 10],
    std_in=[0.02, 0],
    mu=[2.5, 5]
)
model = RNNWWD(input_size, node_size, batch_size, step_size, tr, sc, dist, True, par)

data_mean = [ts.T] * num_epoches
data_mean = np.array(data_mean)

# call model fit method
F = Model_fitting(model, data_mean, num_epoches, 1, 1e-3)

# fit data(train)
output_train = F.train()

X0 = 0.45 * np.random.uniform(0, 1, (node_size, 6)) + np.array([0, 0, 0, 1.0, 1.0, 1.0])
hE0 = np.random.uniform(0, 5, (node_size, 500))
base_batch_num = 20
output_test = F.test(X0, hE0, base_batch_num)
fc_test = np.corrcoef(F.output_sim.bold_test)

fig, ax = plt.subplots(1, 3, figsize=(12, 8))
ax[1].imshow(fc_emp - np.diag(np.diag(fc_emp)), cmap='bwr')
ax[1].set_title('Empirical FC')
ax[0].plot(F.output_sim.bold_test.T)
ax[0].set_title('Test')
ax[2].imshow(fc_test - np.diag(np.diag(fc_test)), cmap='bwr')
ax[2].set_title('Test FC')
plt.show()

end_time = time.time()
print('running time is  {0} \'s'.format(end_time - start_time))
