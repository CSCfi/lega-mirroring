import hashlib, os



# This function generates  an md5 hash for a given file and saves it to a text file
def md5(path):
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
        path = path + '.md5'
        file = open(path, 'w')
        file.write(hash_md5.hexdigest())
        file.close()
    print(path, ' created')
    return

path = 'C:\\Users\\tekataja\\Desktop\\ELIXIR\\bigdir'

for filename in os.listdir(path):
    if filename.endswith('.txt'):
        #print(os.path.join(path, filename)) # prints dir/filename
        #print(filename)
        md5(filename)
