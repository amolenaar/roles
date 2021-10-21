'''

  >>> The following is only an excerpt, showcasing an idea for a possible way of using roles
  >>> it is not in running order
  
'''


class TransferMoney(metaclass=Context):
  '''
    The Context metaclass will need to be written first.
    
    Its task is going to be e.g.: 
    - providing the context mechanism
    - asserting that all used roles are implemented as classes 
    - asserting that all roles have an object assigned before they are accessed
  '''
  
                                          
  ''' Roles '''
  
  class MoneySource(metaclass=RoleType):
      def transfer(self: Account, amount):
          if self.balance >= amount:
              self.withdraw(amount)                    # this role is able to interact with the Account object it's been assigned to
              
              ''' the context keyword serves in a similar way as the self keyword, but addressing the (outer) context scope '''
              context.MoneySink.receive(amount)        # this role interacts here with another role through that role's interface
              
              '''
                ! invalid, should result in an error:
                a) context.sink.deposit(amount)
                b) context.MoneySink.deposit(amount)   # objects assigned to a role should not be directly accessible through the context
              '''
  
  
  class MoneySink(metaclass=RoleType):
      def receive(self: Account, amount):
          self.deposit(amount)                         # this role is able to interact with the Account object it's been assigned to
  
  
  ''' Context definition '''

  def __init__(self, source: Account, sink: Account):
    ''' Role assignment takes place as follows and is handled by the Context metaclass '''
      self.MoneySource = source
      self.MoneySink = sink
  
  def perform_transfer(self, amount):
      ''' 
        It is already declared above and thus clear, that the TransferMoney-object is the context,
        which can be used here immediately without the need of a contextmanager.
      '''
      self.MoneySource.transfer(amount)

      print("We can still access the original attributes", self.MoneySink.balance)    # this should only be possible, if the role implements a balance accessor 
      
      ''' th following will need to be handled by the Context metaclass '''
      print("Is it still an Account?", isinstance(self.MoneySink, PaymentAccount))
      assert isinstance(self.MoneySink, PaymentAccount)
      print("Object equality?", dst == self.MoneySink)
