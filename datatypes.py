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