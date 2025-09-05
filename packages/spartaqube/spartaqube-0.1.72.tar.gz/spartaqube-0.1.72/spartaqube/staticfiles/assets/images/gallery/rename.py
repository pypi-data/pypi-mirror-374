import os
directory = './'
directory = os.path.dirname(os.path.abspath(__file__))
for filename in os.listdir(directory):
    print(filename)
    old_path = os.path.join(directory, filename)
    new_path = os.path.join(directory, filename.replace('.PNG', '.png').replace('-min', ''))
    os.rename(old_path, new_path)
    print(f'Renamed: {old_path} to {new_path}')

#END OF QUBE
