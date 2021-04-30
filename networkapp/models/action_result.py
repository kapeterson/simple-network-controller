
class action_result():

    def __init__(self, success:int, error:int, errmsg:str=None):
        self.success = success
        self.error = error
        self.errmsg = errmsg
        self.data = ""

    def __str__(self):
        return {
            "success" : self.success,
            "error" : self.error,
            "errormsg" : self.errmsg,
            "data" : self.data
        }