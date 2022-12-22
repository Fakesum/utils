class RoundTable(list):
    import typing as __typing
    shift: int = 1
    prev: int = 0

    def get(self, num: int, iterations) -> __typing.Any:
        self.prev = iterations % self.__len__()

        if num >= 6: #Hacky but very well working weird quirky fix
            num += 1
        
        if (self[self.prev:num+self.prev].__len__() < num):
            q, r = divmod(num+self.prev, self.__len__())
            nlist = q*self+self[:r]
            if nlist.__len__() >= num:
                return nlist[nlist.__len__() - num: -1]
            else:
                return nlist
        else:
            return self[self.prev:num+self.prev]

class __TempAssets(object):
    import os as __os
    import typing as __typing
    def __init__(
            self, 
            contents: __typing.Any,
            name: str,
        ) -> None:
        self.contents = contents
        self.img = None
        
        self.name = name
    
    def __enter__(self):
        self.write(self.contents)
        return self
    
    def __exit__(self):
        self.__os.remove(self.name)
    
    def write(self):
        raise NotImplementedError
    
    def read(self):
        raise NotImplementedError

class TempImage(__TempAssets):
    import cv2 as __cv2
    import random as __random
    def __init__(self, contents: __cv2.Mat, name: str = f"temp{__random.randint(10**3,10**4)}") -> None:
        import pathlib
        super().__init__(contents, "png", self.__os.path.join(pathlib.Path(__file__).parent.parent.resolve(),f"assets/temp/imgs/{name}.png"))
    
    def read(self):
        return self.__cv2.imread(self.name)
    
    def write(self,contents):
        self.contents = contents
        self.__cv2.imwrite(self.name, contents)