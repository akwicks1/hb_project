def find_labels(filename):
	"""List of breeds for breed chart."""

	label_list = []
	with open(filename, 'r+') as f:
		lines = f.readlines()
		for line in lines:
			line = line.strip().split("\t")
			line[1] = ("").join(line[1].split(","))
			if int(line[1]) > 1000:
				labels = line[0]
				label_list.append(labels)
		return label_list


find_labels('breeds.csv')

def find_datasets(filename):
	"""Count of breeds for breed chart."""

	dataset_list = []
	with open(filename, 'r+') as f:
		lines = f.readlines()
		for line in lines:
			line = line.strip().split("\t")
			line[1] = ("").join(line[1].split(","))
			datasets = line[1]
			if int(datasets) > 1000:
				dataset_list.append(datasets)
		return dataset_list
			

find_datasets('breeds.csv')
