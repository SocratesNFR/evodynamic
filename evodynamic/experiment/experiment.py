""" Experiment """

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
from . import monitor
from . import memory
from .. import cells
from .. import utils

class Experiment(object):
  def __init__(self, dt: float = 1.0, input_start=0, input_delay=0,\
               training_start=0, training_delay=0, batch_size=1,\
               reset_cells_after_train=False, reset_memories_after_train=False) -> None:
    tf.reset_default_graph()
    self.dt = dt
    self.cell_groups = {}
    self.connections = {}
    self.connection_list = []
    self.trainable_connections = {}
    self.connection_ops = []
    self.input_name_list = []
    self.input_ops = []
    self.train_ops = []
    self.monitors = {}
    self.session = tf.Session()
    self.memories = {}
    self.step_counter = 0
    self.memory_counter = 0
    self.input_start = input_start
    self.input_delay = input_delay
    self.input_tracker = -1
    self.training_start = training_start
    self.training_delay = training_delay
    self.training_tracker = -1
    self.experiment_output = {}
    self.has_input = tf.placeholder(tf.bool, shape=())
    self.training_loss_op = None
    self.training_loss = 9999999
    self.batch_size = batch_size
    self.reset_cells_after_train = reset_cells_after_train
    self.reset_memories_after_train = reset_memories_after_train

  def add_input(self, dtype, shape, name):
    shape_with_batch = list(shape)
    shape_with_batch.insert(1,self.batch_size)
    input_placeholder = tf.placeholder(dtype, shape=shape_with_batch, name=name)
    self.input_name_list.append(name)
    return input_placeholder

  def add_group_cells(self, name, amount, virtual_shape=None):
    g_cells = cells.Cells(amount, self.batch_size, virtual_shape)
    self.cell_groups[name] = g_cells
    return g_cells

  def add_state_memory(self, state, memory_size):
    state_memory = memory.Memory(self,state,memory_size)
    self.memories[state] = state_memory
    return state_memory.get_op()

  def update_experiment_output(self, new_connection):
    if new_connection.from_group in self.experiment_output and\
      new_connection.to_group not in self.experiment_output:
      del self.experiment_output[new_connection.from_group]

    self.experiment_output[new_connection.to_group] = new_connection

  def add_connection(self, name, connection):
    connection.set_experiment(self)
    self.connections[name] = connection
    self.connection_list.insert(0,connection)
    self.connection_ops.append(connection.list_ops)
    self.update_experiment_output(connection)
    if connection.from_group.name.split(":")[0] in self.input_name_list: # if input
      self.input_ops.append(connection.list_ops)
    else:
      self.connection_ops.append(connection.list_ops)
    return connection

  def add_trainable_connection(self, name, connection):
    self.add_connection(name, connection)
    self.trainable_connections[name] = connection
    return connection

  def initialize_cells(self):
    self.session.run(tf.global_variables_initializer())
    for monitor_key in self.monitors:
      self.monitors[monitor_key].initialize()

  def reset_cell_states(self):
    for cell_group_key in self.cell_groups:
      for state_key in self.cell_groups[cell_group_key].states:
        state = self.cell_groups[cell_group_key].states[state_key]
        self.session.run(tf.assign(state, tf.zeros_like(state)))

  def set_training(self, loss, learning_rate, optimizer="adam"):
    model_vars = tf.trainable_variables()
    self.training_loss_op = loss
    t_vars = []
    for var in model_vars:
      for conn_key in self.trainable_connections:
        if conn_key in var.name:
          t_vars.append(var)

    if optimizer == "adam":
      #train_op = tf.train.AdamOptimizer(learning_rate, beta1=0, beta2=0).minimize(loss, var_list=t_vars)
      train_op = tf.train.AdamOptimizer(learning_rate).minimize(loss, var_list=t_vars)
    else:
      print("set_training has set invalid optimizer")

    self.train_ops.append(train_op)

  def close(self):
    self.session.close()

  def is_input_step(self):
    return ((self.step_counter-self.input_start) // (self.input_delay+1)) > self.input_tracker

  def is_training_step(self):
    return ((self.step_counter-self.training_start) // (self.training_delay+1)) > self.training_tracker

  def run(self,timesteps: int = 10):
    for step in range(timesteps-1):
      self.run_step()
      utils.progressbar(step+1, timesteps-1)

  def run_with_input_list(self, timesteps: int, feed_dict_list):
    feed_counter = 0
    for step in range(timesteps-1):
      if self.is_input_step() or self.is_training_step():
        self.run_step(feed_dict=feed_dict_list[feed_counter])
        feed_counter += 1
      else:
        self.run_step()
      utils.progressbar(step+1, timesteps-1)

  def run_with_input_generator(self, timesteps: int, generator):
    for step in range(timesteps-1):
      if self.is_input_step() or self.is_training_step():

        feed_dict = generator(self.step_counter)
        self.run_step(feed_dict=feed_dict)
      else:
        self.run_step()
      utils.progressbar(step+1, timesteps-1)

  def run_step(self, feed_dict=None):
    if not feed_dict:
      feed_dict = {}
    feed_dict[self.has_input] = False
    if self.is_input_step():
      feed_dict[self.has_input] = True
      self.input_tracker += 1

    for experiment_output_key in self.experiment_output:
      self.session.run(self.experiment_output[experiment_output_key].assign_output,feed_dict=feed_dict)

    for memory_key in self.memories:
      self.memories[memory_key].update_state_memory()

    for monitor_key in self.monitors:
      self.monitors[monitor_key].record()

    if self.is_training_step():
      train_result = self.session.run(self.train_ops + [self.training_loss_op], feed_dict=feed_dict)
      print("train_result", train_result)
      #print("train_loss", train_result[-1])
      self.training_loss = train_result[-1]
      self.training_tracker += 1
      if self.reset_cells_after_train:
        self.reset_cell_states()
      if self.reset_memories_after_train:
        self.memory_counter = 0
        for memory_key in self.memories:
          self.memories[memory_key].reset()
    self.step_counter += 1
    self.memory_counter += 1

  def check_group_cells_state(self, group_cells_name, state_name):
    group_cells_name_exists = group_cells_name in self.cell_groups
    assert group_cells_name_exists, "Error: group_cells_name for group_cells does not exist."

    state_name_exists = state_name in self.cell_groups[group_cells_name].states
    assert state_name_exists, "Error: state_name for state does not exist."

  def get_group_cells_state(self, group_cells_name, state_name):
    self.check_group_cells_state(group_cells_name, state_name)

    return self.session.run(self.cell_groups[group_cells_name].states[state_name])

  def add_monitor(self, group_cells_name, state_name, timesteps=None):
    self.check_group_cells_state(group_cells_name, state_name)

    self.monitors[(group_cells_name,state_name)] =\
      monitor.Monitor(self, group_cells_name, state_name, duration=timesteps)

  def get_monitor(self, group_cells_name, state_name):
    self.check_group_cells_state(group_cells_name, state_name)

    return self.monitors[(group_cells_name,state_name)].get()

  def get_connection(self, conn_name):
    conn_name_exists = conn_name in self.connections
    assert conn_name_exists, "Error: conn_name for connections does not exist."

    return self.connections[conn_name]