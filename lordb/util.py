import random


phrases = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit" ,
    "Pellentesque in diam cursus, convallis nisl quis, pulvinar sapien" ,
    "Donec id lacus nec leo ullamcorper auctor auctor eu elit" ,
    "Curabitur imperdiet urna nec ligula tristique pulvinar" ,
    "Proin euismod nisi vel risus tempor, condimentum sodales ipsum vehicula" ,
    "Praesent sit amet justo sed metus lacinia congue" ,
    "Nunc ut neque vel arcu dictum ornare eget vitae erat" ,
    "Etiam nec sem eget ipsum ullamcorper auctor sit amet vitae nulla" ,
    "Sed id lorem id velit tincidunt semper eu ac dui" ,
    "Sed nec lorem sagittis, elementum odio eget, vehicula quam" ,
    "Donec non magna mollis, sollicitudin justo id, lacinia justo" ,
    "In ullamcorper elit pretium tincidunt ultrices" ,
    "Quisque blandit velit ut erat iaculis, quis tristique massa volutpat" ,
    "Sed eu nisi rutrum, faucibus eros vel, hendrerit nisi" ,
    "Morbi pretium risus ac libero posuere ultricies" ,
    "Maecenas varius urna quis consequat accumsan" ,
    "Suspendisse luctus est et magna lacinia, quis placerat ligula aliquet" ,
    "Nullam bibendum lacus ultrices, cursus ipsum at, euismod nunc" ,
    "Fusce ac metus feugiat, sodales tellus at, tincidunt leo" ,
    "Sed tempor nulla a eleifend tempor" ,
    "Nulla porttitor dui at sollicitudin porta" ,
    "Phasellus ut odio sed magna varius facilisis ut quis diam" ,
    "Cras quis neque ut mi iaculis fringilla" ,
    "Ut posuere enim ac ante laoreet commodo" ,
    "Proin convallis nulla eu arcu consequat, id pellentesque nibh ultrices" ,
    "Mauris iaculis nulla nec eros accumsan suscipit" ,
    "Suspendisse vel urna eu sem commodo viverra" ,
    "Nunc eu neque pretium, adipiscing enim ut, bibendum urna" ,
    "Maecenas et metus et ligula luctus faucibus" ,
    "Vivamus ullamcorper dui nec diam gravida, sed semper mi tristique" ,
    "Suspendisse adipiscing nibh at lacus condimentum, et fermentum ante eleifend" ,
    "Donec blandit elit id libero consectetur, nec congue est hendrerit" ,
    "Integer ac quam vel erat tincidunt rhoncus ut ac elit" ,
    "Sed et erat a mauris convallis pretium non in mi" ,
    "Nam sed nunc et ante rhoncus interdum ut eu odio" ,
    "Phasellus condimentum purus eu libero rhoncus vehicula" ,
    "Vivamus luctus tellus sit amet sem pellentesque placerat at ac lorem" ,
    "Nulla pellentesque justo ut urna tempus, sed ultrices tortor tempor" ,
    "Integer ut ligula iaculis, pellentesque tellus non, condimentum tellus" ,
    "Mauris volutpat tellus in diam lobortis tempor" ,
    "Fusce nec felis id erat fermentum rhoncus" ,
    "Vestibulum eget erat et dui sollicitudin semper" ,
]

class ContentGen:
    def get_text(self, max_len):
        phrase = self.get_in_list(phrases)

        if len(phrase) > max_len:
            return phrase[0:random.randint(1, max_len)]

        return phrase

    def get_in_list(self, list):
        return list[self.get_int(0, len(list)-1)]

    def get_int(self, start, end):
        return random.randint(start, end)