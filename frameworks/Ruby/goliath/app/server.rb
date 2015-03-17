require 'goliath'

class Hello < Goliath::API
  def response(env)
    [200, {}, "Hello, world!"]
  end
end