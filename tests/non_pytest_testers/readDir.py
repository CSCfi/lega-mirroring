import os

print('1')




path = 'C:\\Users\\tekataja\\Desktop\\ELIXIR\\bigdir'

for filename in os.listdir(path):
    if filename.endswith('.txt'):
        #print(os.path.join(path, filename)) # prints dir/filename
        print(filename)
        
        




print('2')
