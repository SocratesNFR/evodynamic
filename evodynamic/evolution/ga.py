""" Genetic algorithm """

import numpy as np
import random
import time
import csv
# Generate random genomes
# Evaluate genomes
# Select genomes and reproduce them

# Code based on https://github.com/PytLab/gaft/blob/master/gaft

def evolve_rules(evaluate_genome, pop_size=10, generation=4, gene_range=[0,255]):
  assert pop_size%2==0, "Error: pop_size must be even!"
  timestr = time.strftime("%Y%m%d-%H%M%S")

  filehistory = open("evo_rules_"+timestr+".txt", "w")
  
  wr = csv.writer(filehistory, delimiter=";")
  wr.writerow(["generation", "fitness", "val_dict", "genome"])


  prob_crossover = 0.8
  prob_exchange = 0.5
  prob_mutate_gene = 0.1
  prob_add_gene = 0.1
  prob_delete_gene = 0.1

  pop_indices = list(range(pop_size))
  pop_list = [[np.random.randint(gene_range[0], gene_range[1]+1) for gene in range(np.random.randint(1,5))] for pop in range(pop_size)]
  fitness_list = []
  val_dict_list = []
  for genome in pop_list:
    fitness_score, val_dict = evaluate_genome(genome)
    fitness_list.append(fitness_score)
    val_dict_list.append(val_dict)
    wr.writerow(["0", str(fitness_score), str(val_dict), str(genome)])

  best_genome_idx = max(pop_indices, key=lambda idx: fitness_list[idx])
  best_genome = list(pop_list[best_genome_idx])
  best_genome_fitness = fitness_list[best_genome_idx]
  best_val_dict = dict(val_dict_list[best_genome_idx])

  for gen in range(generation):
    new_pop_list = []
    new_fitness_list = []
    new_val_dict_list = []
    for _ in range(pop_size//2):
      # Tournament selection
      group1 = random.sample(pop_indices, 2)
      group2 = random.sample(pop_indices, 2)

      selected1 = max(group1, key=lambda idx: fitness_list[idx])
      selected2 = max(group2, key=lambda idx: fitness_list[idx])

      genome1 = pop_list[selected1]
      genome2 = pop_list[selected2]

      for i, (gene1, gene2) in enumerate(zip(genome1, genome2)):
        # Crossover
        if prob_crossover > np.random.random():
          # Exchange of genes
          if prob_exchange > np.random.random():
            genome1[i] = gene2
            genome2[i] = gene1

        # Mutate gene 1
        if prob_mutate_gene > np.random.random():
          genome1[i] = (genome1[i] + np.random.randint(-25, 26)) % 255

         # Mutate gene 2
        if prob_mutate_gene > np.random.random():
          genome2[i] = (genome2[i] + np.random.randint(-25, 26)) % 255

      # Add gene to genome 1
      if prob_add_gene > np.random.random():
        genome1.append(np.random.randint(gene_range[0], gene_range[1]+1))

      # Add gene to genome 2
      if prob_add_gene > np.random.random():
        genome2.append(np.random.randint(gene_range[0], gene_range[1]+1))

      # Delete gene from genome 1
      if prob_delete_gene > np.random.random() and len(genome1)>1:
        del genome1[np.random.randint(len(genome1))]

      # Delete gene from genome 2
      if prob_delete_gene > np.random.random() and len(genome2)>1:
        del genome2[np.random.randint(len(genome2))]

      # Add new genomes for next generation
      new_pop_list.append(genome1)
      new_pop_list.append(genome2)

      # Evaluate new genomes
      fitness_genome1, val_dict1 = evaluate_genome(genome1)
      fitness_genome2, val_dict2 = evaluate_genome(genome2)

      new_fitness_list.append(fitness_genome1)
      new_fitness_list.append(fitness_genome2)
      
      new_val_dict_list.append(val_dict1)
      new_val_dict_list.append(val_dict2)

      wr.writerow([str(gen+1), str(fitness_genome1), str(val_dict1), str(genome1)])
      wr.writerow([str(gen+1), str(fitness_genome2), str(val_dict2), str(genome2)])

    pop_list = list(new_pop_list)
    fitness_list = list(new_fitness_list)
    val_dict_list = list(new_val_dict_list)
    generation_best_genome_idx = max(pop_indices, key=lambda idx: fitness_list[idx])
    
#    for ii, pf in enumerate(zip(fitness_list, pop_list)):
#      print("GENERATION", ii, pf[0], pf[1])
    
    if fitness_list[generation_best_genome_idx] > best_genome_fitness:
      best_genome = list(pop_list[generation_best_genome_idx])
      best_genome_fitness = fitness_list[generation_best_genome_idx]
      best_val_dict = dict(val_dict_list[generation_best_genome_idx])

      print("PARTIAL generation_best_genome_idx", generation_best_genome_idx)
      print("PARTIAL best_genome", best_genome)
      print("PARTIAL new_pop_list[generation_best_genome_idx]", new_pop_list[generation_best_genome_idx])
      print("PARTIAL best_genome_fitness", best_genome_fitness)
      print("PARTIAL new_fitness_list[idx]", new_fitness_list[generation_best_genome_idx])
      print("PARTIAL new_pop_list[generation_best_genome_idx]", new_pop_list[generation_best_genome_idx])
      print("PARTIAL best_val_dict", best_val_dict)

  print("best_genome", best_genome)
  print("best_genome_fitness", best_genome_fitness)
  print("best_val_dict", best_val_dict)

  return best_genome

def evolve_probability(evaluate_genome, pop_size=10, generation=10, prob_size=8):
  assert pop_size%2==0, "Error: pop_size must be even!"
  timestr = time.strftime("%Y%m%d-%H%M%S")
  
  filehistory = open("evo_prob_"+timestr+".txt", "w")

  wr = csv.writer(filehistory, delimiter=";")
  wr.writerow(["generation", "fitness", "val_dict", "genome"])

  prob_crossover = 0.8
  prob_exchange = 0.5
  prob_mutate_gene = 0.1

  pop_indices = list(range(pop_size))
  pop_list = [[np.random.rand() for gene in range(prob_size)] for pop in range(pop_size)]
  fitness_list = []
  val_dict_list = []
  for genome in pop_list:
    fitness_score, val_dict = evaluate_genome(genome)
    fitness_list.append(fitness_score)
    val_dict_list.append(val_dict)
    wr.writerow(["0", str(fitness_score), str(val_dict), str(genome)])

  best_genome_idx = max(pop_indices, key=lambda idx: fitness_list[idx])
  best_genome = list(pop_list[best_genome_idx])
  best_genome_fitness = fitness_list[best_genome_idx]
  best_val_dict = dict(val_dict_list[best_genome_idx])

  for gen in range(generation):
    new_pop_list = []
    new_fitness_list = []
    new_val_dict_list = []
    for _ in range(pop_size//2):
      # Tournament selection
      group1 = random.sample(pop_indices, 2)
      group2 = random.sample(pop_indices, 2)

      selected1 = max(group1, key=lambda idx: fitness_list[idx])
      selected2 = max(group2, key=lambda idx: fitness_list[idx])

      genome1 = pop_list[selected1]
      genome2 = pop_list[selected2]

      for i, (gene1, gene2) in enumerate(zip(genome1, genome2)):
        # Crossover
        if prob_crossover > np.random.random():
          # Exchange of genes
          if prob_exchange > np.random.random():
            genome1[i] = gene2
            genome2[i] = gene1

        # Mutate gene 1
        if prob_mutate_gene > np.random.random():
          genome1[i] = np.clip(genome1[i] + np.random.normal(scale=0.2), 0.,1.)

         # Mutate gene 2
        if prob_mutate_gene > np.random.random():
          genome2[i] = np.clip(genome2[i] + np.random.normal(scale=0.2), 0.,1.)

      # Add new genomes for next generation
      new_pop_list.append(genome1)
      new_pop_list.append(genome2)

      # Evaluate new genomes
      fitness_genome1, val_dict1 = evaluate_genome(genome1)
      fitness_genome2, val_dict2 = evaluate_genome(genome2)

      new_fitness_list.append(fitness_genome1)
      new_fitness_list.append(fitness_genome2)

      new_val_dict_list.append(val_dict1)
      new_val_dict_list.append(val_dict2)

      wr.writerow([str(gen+1), str(fitness_genome1), str(val_dict1), str(genome1)])
      wr.writerow([str(gen+1), str(fitness_genome2), str(val_dict2), str(genome2)])

    pop_list = list(new_pop_list)
    fitness_list = list(new_fitness_list)
    val_dict_list = list(new_val_dict_list)
    generation_best_genome_idx = max(pop_indices, key=lambda idx: fitness_list[idx])

#    for ii, pf in enumerate(zip(fitness_list, pop_list)):
#      print("GENERATION", ii, pf[0], pf[1])

    if fitness_list[generation_best_genome_idx] > best_genome_fitness:
      best_genome = list(pop_list[generation_best_genome_idx])
      best_genome_fitness = fitness_list[generation_best_genome_idx]
      best_val_dict = dict(val_dict_list[generation_best_genome_idx])
      print("PARTIAL generation_best_genome_idx", generation_best_genome_idx)
      print("PARTIAL best_genome", best_genome)
      print("PARTIAL new_pop_list[generation_best_genome_idx]", new_pop_list[generation_best_genome_idx])
      print("PARTIAL best_genome_fitness", best_genome_fitness)
      print("PARTIAL new_fitness_list[idx]", new_fitness_list[generation_best_genome_idx])
      print("PARTIAL best_val_dict", best_val_dict)

  print("best_genome", best_genome)
  print("best_genome_fitness", best_genome_fitness)
  print("best_val_dict", best_val_dict)
  filehistory.close()
  return best_genome









