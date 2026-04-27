How each learning standard is addressed





B3.1.1 — OOP concepts are named explicitly in docstrings (encapsulation, inheritance, abstraction, polymorphism)



B3.1.2 — Students design their paddle class with clear method responsibilities; the Chaser/Predictor scaffolding shows class design at two levels before they attempt their own



B3.1.3 — NAME is a class variable (accessed as PaddleClass.NAME); self.get_y() is instance state; contrast is called out explicitly in the template



B3.1.4 — Students write a full class definition with __init__, override methods, instantiate via the engine



B3.1.5 — __x/__y name-mangling enforces private access; get_y()/set_y() are classic getters/setters; OpponentView demonstrates information hiding; my_score/opponent_score show @property



B3.2.1 — Students inherit Paddle; premade paddles show the same base being reused for different behaviours; super().__init__() is a required, visible call



B3.2.2 — Students override tick() and __init__; three premade paddles override the same method with different logic — direct polymorphism demonstration



B3.2.3 — Paddle is an ABC with @abstractmethod tick(); students cannot instantiate it directly



B3.2.4 — Paddle has-a Field (aggregation — field exists independently); PongSimulator has-a Ball (composition — simulator creates and owns it); discussed via explanation/annotation rather than new code



B3.2.5 — Template Method pattern (engine calls tick()) and Observer/Hook pattern (lifecycle hooks) are named explicitly in docstrings