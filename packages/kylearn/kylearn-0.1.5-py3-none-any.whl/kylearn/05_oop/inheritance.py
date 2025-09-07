"""
面向对象编程 - 继承示例

本模块演示Python中继承的概念和用法，包括：
1. 单继承的基本用法
2. 方法重写(Override)
3. super()函数的使用
4. 多继承和方法解析顺序(MRO)
5. 继承层次设计的最佳实践
"""


# ============================================================================
# 1. 单继承基础示例
# ============================================================================

class Animal:
    """
    动物基类 - 演示继承的基础概念
    """
    
    def __init__(self, name, species):
        """
        构造函数
        
        Args:
            name (str): 动物名称
            species (str): 物种
        """
        self.name = name
        self.species = species
        self.is_alive = True
    
    def eat(self, food):
        """
        吃东西
        
        Args:
            food (str): 食物名称
        """
        print(f"{self.name}正在吃{food}")
    
    def sleep(self):
        """睡觉"""
        print(f"{self.name}正在睡觉")
    
    def make_sound(self):
        """
        发出声音 - 基类提供默认实现
        """
        print(f"{self.name}发出了声音")
    
    def get_info(self):
        """
        获取动物信息
        
        Returns:
            str: 动物信息
        """
        status = "活着" if self.is_alive else "已死亡"
        return f"名称：{self.name}，物种：{self.species}，状态：{status}"
    
    def __str__(self):
        """字符串表示"""
        return f"{self.species}：{self.name}"


class Dog(Animal):
    """
    狗类 - 继承自Animal类
    """
    
    def __init__(self, name, breed, owner=None):
        """
        构造函数
        
        Args:
            name (str): 狗的名字
            breed (str): 品种
            owner (str): 主人姓名，可选
        """
        # 调用父类构造函数
        super().__init__(name, "犬科")
        self.breed = breed
        self.owner = owner
        self.tricks = []  # 会的技能列表
    
    def make_sound(self):
        """
        重写父类方法 - 狗的叫声
        """
        print(f"{self.name}汪汪叫")
    
    def wag_tail(self):
        """
        摇尾巴 - 狗特有的行为
        """
        print(f"{self.name}开心地摇尾巴")
    
    def learn_trick(self, trick):
        """
        学习技能
        
        Args:
            trick (str): 技能名称
        """
        if trick not in self.tricks:
            self.tricks.append(trick)
            print(f"{self.name}学会了新技能：{trick}")
        else:
            print(f"{self.name}已经会{trick}了")
    
    def perform_trick(self, trick):
        """
        表演技能
        
        Args:
            trick (str): 技能名称
        """
        if trick in self.tricks:
            print(f"{self.name}表演了{trick}！")
        else:
            print(f"{self.name}还不会{trick}")
    
    def get_info(self):
        """
        重写父类方法 - 获取狗的详细信息
        """
        base_info = super().get_info()  # 调用父类方法
        owner_info = f"，主人：{self.owner}" if self.owner else "，无主人"
        tricks_info = f"，技能：{', '.join(self.tricks)}" if self.tricks else "，无技能"
        return f"{base_info}，品种：{self.breed}{owner_info}{tricks_info}"


class Cat(Animal):
    """
    猫类 - 继承自Animal类
    """
    
    def __init__(self, name, color, is_indoor=True):
        """
        构造函数
        
        Args:
            name (str): 猫的名字
            color (str): 毛色
            is_indoor (bool): 是否为室内猫
        """
        super().__init__(name, "猫科")
        self.color = color
        self.is_indoor = is_indoor
        self.mood = "平静"  # 心情状态
    
    def make_sound(self):
        """
        重写父类方法 - 猫的叫声
        """
        print(f"{self.name}喵喵叫")
    
    def purr(self):
        """
        呼噜声 - 猫特有的行为
        """
        print(f"{self.name}发出满足的呼噜声")
        self.mood = "开心"
    
    def scratch(self, target="抓板"):
        """
        抓挠
        
        Args:
            target (str): 抓挠的目标
        """
        print(f"{self.name}在{target}上磨爪子")
    
    def hunt(self):
        """
        狩猎行为
        """
        if not self.is_indoor:
            print(f"{self.name}在外面狩猎")
            self.mood = "兴奋"
        else:
            print(f"{self.name}在家里追逐玩具")
            self.mood = "活跃"
    
    def get_info(self):
        """
        重写父类方法 - 获取猫的详细信息
        """
        base_info = super().get_info()
        location = "室内" if self.is_indoor else "室外"
        return f"{base_info}，毛色：{self.color}，生活环境：{location}，心情：{self.mood}"


def demo_basic_inheritance():
    """演示基本继承概念"""
    print("=== 基本继承示例 ===")
    
    # 创建动物实例
    animal = Animal("通用动物", "未知")
    dog = Dog("旺财", "金毛", "张三")
    cat = Cat("咪咪", "橘色", True)
    
    print("=== 基类Animal ===")
    print(animal.get_info())
    animal.make_sound()
    animal.eat("食物")
    
    print("\n=== 子类Dog ===")
    print(dog.get_info())
    dog.make_sound()  # 重写的方法
    dog.eat("狗粮")   # 继承的方法
    dog.wag_tail()    # 子类特有方法
    dog.learn_trick("坐下")
    dog.learn_trick("握手")
    dog.perform_trick("坐下")
    print(dog.get_info())
    
    print("\n=== 子类Cat ===")
    print(cat.get_info())
    cat.make_sound()  # 重写的方法
    cat.eat("猫粮")   # 继承的方法
    cat.purr()        # 子类特有方法
    cat.scratch("沙发")
    cat.hunt()
    print(cat.get_info())
    
    print()


# ============================================================================
# 2. super()函数的详细使用
# ============================================================================

class Vehicle:
    """
    交通工具基类 - 演示super()的使用
    """
    
    def __init__(self, brand, model, year):
        """
        构造函数
        
        Args:
            brand (str): 品牌
            model (str): 型号
            year (int): 年份
        """
        self.brand = brand
        self.model = model
        self.year = year
        self.is_running = False
        print(f"Vehicle初始化：{brand} {model} ({year})")
    
    def start(self):
        """启动"""
        if not self.is_running:
            self.is_running = True
            print(f"{self.brand} {self.model}启动了")
        else:
            print(f"{self.brand} {self.model}已经在运行中")
    
    def stop(self):
        """停止"""
        if self.is_running:
            self.is_running = False
            print(f"{self.brand} {self.model}停止了")
        else:
            print(f"{self.brand} {self.model}已经停止")
    
    def get_info(self):
        """获取车辆信息"""
        status = "运行中" if self.is_running else "停止"
        return f"{self.brand} {self.model} ({self.year}) - 状态：{status}"


class Car(Vehicle):
    """
    汽车类 - 演示super()在单继承中的使用
    """
    
    def __init__(self, brand, model, year, fuel_type, doors=4):
        """
        构造函数
        
        Args:
            brand (str): 品牌
            model (str): 型号
            year (int): 年份
            fuel_type (str): 燃料类型
            doors (int): 门数
        """
        # 调用父类构造函数
        super().__init__(brand, model, year)
        self.fuel_type = fuel_type
        self.doors = doors
        self.fuel_level = 100  # 燃料水平
        print(f"Car初始化：{fuel_type}燃料，{doors}门")
    
    def start(self):
        """
        重写启动方法 - 添加燃料检查
        """
        if self.fuel_level <= 0:
            print(f"{self.brand} {self.model}燃料不足，无法启动")
            return
        
        print("检查燃料...")
        print(f"燃料充足({self.fuel_level}%)")
        super().start()  # 调用父类的start方法
    
    def drive(self, distance):
        """
        驾驶
        
        Args:
            distance (int): 行驶距离(公里)
        """
        if not self.is_running:
            print("请先启动车辆")
            return
        
        fuel_consumption = distance * 0.1  # 每公里消耗0.1%燃料
        if self.fuel_level < fuel_consumption:
            print("燃料不足，无法完成行程")
            return
        
        self.fuel_level -= fuel_consumption
        print(f"行驶了{distance}公里，剩余燃料：{self.fuel_level:.1f}%")
    
    def refuel(self):
        """加油"""
        self.fuel_level = 100
        print(f"{self.brand} {self.model}加满油了")
    
    def get_info(self):
        """
        重写获取信息方法
        """
        base_info = super().get_info()  # 调用父类方法
        return f"{base_info}，燃料类型：{self.fuel_type}，门数：{self.doors}，燃料：{self.fuel_level:.1f}%"


class ElectricCar(Car):
    """
    电动汽车类 - 演示多层继承中super()的使用
    """
    
    def __init__(self, brand, model, year, battery_capacity, doors=4):
        """
        构造函数
        
        Args:
            brand (str): 品牌
            model (str): 型号
            year (int): 年份
            battery_capacity (int): 电池容量(kWh)
            doors (int): 门数
        """
        # 调用父类构造函数，传入"电力"作为燃料类型
        super().__init__(brand, model, year, "电力", doors)
        self.battery_capacity = battery_capacity
        self.charge_level = 100  # 电量水平
        print(f"ElectricCar初始化：电池容量{battery_capacity}kWh")
    
    def start(self):
        """
        重写启动方法 - 电动车特有的启动过程
        """
        if self.charge_level <= 0:
            print(f"{self.brand} {self.model}电量不足，无法启动")
            return
        
        print("检查电池...")
        print(f"电量充足({self.charge_level}%)")
        # 跳过Car的start方法，直接调用Vehicle的start方法
        Vehicle.start(self)
        print("电动系统就绪")
    
    def drive(self, distance):
        """
        重写驾驶方法 - 使用电量而不是燃料
        """
        if not self.is_running:
            print("请先启动车辆")
            return
        
        power_consumption = distance * 0.15  # 每公里消耗0.15%电量
        if self.charge_level < power_consumption:
            print("电量不足，无法完成行程")
            return
        
        self.charge_level -= power_consumption
        print(f"行驶了{distance}公里，剩余电量：{self.charge_level:.1f}%")
    
    def charge(self, hours):
        """
        充电
        
        Args:
            hours (float): 充电小时数
        """
        charge_rate = 10  # 每小时充电10%
        charge_amount = min(hours * charge_rate, 100 - self.charge_level)
        self.charge_level += charge_amount
        print(f"充电{hours}小时，当前电量：{self.charge_level:.1f}%")
    
    def get_info(self):
        """
        重写获取信息方法
        """
        # 调用Car的get_info，但替换燃料信息为电量信息
        base_info = super().get_info()
        # 替换燃料信息为电量信息
        info_parts = base_info.split("，燃料：")
        if len(info_parts) == 2:
            base_info = info_parts[0] + f"，电量：{self.charge_level:.1f}%"
        return f"{base_info}，电池容量：{self.battery_capacity}kWh"


def demo_super_usage():
    """演示super()函数的使用"""
    print("=== super()函数使用示例 ===")
    
    # 创建不同层次的对象
    print("=== 创建普通汽车 ===")
    car = Car("丰田", "卡罗拉", 2023, "汽油")
    print(car.get_info())
    
    print("\n=== 汽车操作 ===")
    car.start()
    car.drive(50)
    car.stop()
    
    print("\n=== 创建电动汽车 ===")
    electric_car = ElectricCar("特斯拉", "Model 3", 2023, 75)
    print(electric_car.get_info())
    
    print("\n=== 电动汽车操作 ===")
    electric_car.start()
    electric_car.drive(100)
    electric_car.charge(2)
    electric_car.stop()
    
    print()


# ============================================================================
# 3. 多继承和方法解析顺序(MRO)
# ============================================================================

class Flyable:
    """
    可飞行的混入类(Mixin)
    """
    
    def __init__(self):
        """初始化飞行相关属性"""
        self.altitude = 0
        self.max_altitude = 1000
        print("Flyable初始化")
    
    def take_off(self):
        """起飞"""
        if self.altitude == 0:
            self.altitude = 100
            print("起飞成功，当前高度：100米")
        else:
            print("已经在空中")
    
    def land(self):
        """降落"""
        if self.altitude > 0:
            self.altitude = 0
            print("降落成功")
        else:
            print("已经在地面")
    
    def fly_to_altitude(self, target_altitude):
        """
        飞行到指定高度
        
        Args:
            target_altitude (int): 目标高度
        """
        if target_altitude > self.max_altitude:
            print(f"超过最大飞行高度{self.max_altitude}米")
            return
        
        if target_altitude < 0:
            print("高度不能为负数")
            return
        
        self.altitude = target_altitude
        print(f"飞行到{target_altitude}米高度")


class Swimmable:
    """
    可游泳的混入类(Mixin)
    """
    
    def __init__(self):
        """初始化游泳相关属性"""
        self.depth = 0
        self.max_depth = 50
        print("Swimmable初始化")
    
    def dive(self, target_depth):
        """
        潜水
        
        Args:
            target_depth (int): 目标深度
        """
        if target_depth > self.max_depth:
            print(f"超过最大潜水深度{self.max_depth}米")
            return
        
        if target_depth < 0:
            print("深度不能为负数")
            return
        
        self.depth = target_depth
        print(f"潜水到{target_depth}米深度")
    
    def surface(self):
        """浮出水面"""
        if self.depth > 0:
            self.depth = 0
            print("浮出水面")
        else:
            print("已经在水面")


class Duck(Animal, Flyable, Swimmable):
    """
    鸭子类 - 演示多继承
    继承顺序：Animal -> Flyable -> Swimmable
    """
    
    def __init__(self, name, color="白色"):
        """
        构造函数
        
        Args:
            name (str): 鸭子名字
            color (str): 羽毛颜色
        """
        print(f"Duck初始化开始：{name}")
        
        # 初始化所有父类
        Animal.__init__(self, name, "鸭科")
        Flyable.__init__(self)
        Swimmable.__init__(self)
        
        self.color = color
        self.max_altitude = 500  # 鸭子的最大飞行高度较低
        self.max_depth = 10      # 鸭子的最大潜水深度较浅
        
        print(f"Duck初始化完成：{name}")
    
    def make_sound(self):
        """
        重写动物的叫声方法
        """
        print(f"{self.name}嘎嘎叫")
    
    def swim(self):
        """
        游泳 - 鸭子特有的游泳方式
        """
        print(f"{self.name}在水面游泳")
    
    def get_info(self):
        """
        获取鸭子的完整信息
        """
        base_info = Animal.get_info(self)
        location_info = []
        
        if self.altitude > 0:
            location_info.append(f"飞行高度{self.altitude}米")
        if self.depth > 0:
            location_info.append(f"潜水深度{self.depth}米")
        if not location_info:
            location_info.append("在地面/水面")
        
        location = "，".join(location_info)
        return f"{base_info}，颜色：{self.color}，位置：{location}"


class Penguin(Animal, Swimmable):
    """
    企鹅类 - 不能飞行但能游泳的鸟类
    """
    
    def __init__(self, name, height):
        """
        构造函数
        
        Args:
            name (str): 企鹅名字
            height (int): 身高(厘米)
        """
        print(f"Penguin初始化开始：{name}")
        
        Animal.__init__(self, name, "企鹅科")
        Swimmable.__init__(self)
        
        self.height = height
        self.max_depth = 200  # 企鹅潜水能力很强
        
        print(f"Penguin初始化完成：{name}")
    
    def make_sound(self):
        """
        企鹅的叫声
        """
        print(f"{self.name}发出企鹅特有的叫声")
    
    def slide_on_ice(self):
        """
        在冰上滑行 - 企鹅特有行为
        """
        print(f"{self.name}在冰上快速滑行")
    
    def get_info(self):
        """
        获取企鹅信息
        """
        base_info = Animal.get_info(self)
        depth_info = f"潜水深度{self.depth}米" if self.depth > 0 else "在地面/水面"
        return f"{base_info}，身高：{self.height}cm，位置：{depth_info}"


def demo_multiple_inheritance():
    """演示多继承和MRO"""
    print("=== 多继承和方法解析顺序(MRO) ===")
    
    # 查看MRO
    print("Duck类的MRO:")
    for i, cls in enumerate(Duck.__mro__):
        print(f"  {i+1}. {cls.__name__}")
    
    print("\nPenguin类的MRO:")
    for i, cls in enumerate(Penguin.__mro__):
        print(f"  {i+1}. {cls.__name__}")
    
    print("\n=== 创建鸭子 ===")
    duck = Duck("唐老鸭", "黄色")
    print(duck.get_info())
    
    print("\n=== 鸭子的各种行为 ===")
    duck.make_sound()
    duck.swim()
    duck.take_off()
    duck.fly_to_altitude(200)
    duck.dive(5)
    print(duck.get_info())
    duck.surface()
    duck.land()
    
    print("\n=== 创建企鹅 ===")
    penguin = Penguin("波波", 80)
    print(penguin.get_info())
    
    print("\n=== 企鹅的各种行为 ===")
    penguin.make_sound()
    penguin.slide_on_ice()
    penguin.dive(50)
    print(penguin.get_info())
    penguin.surface()
    
    print()


# ============================================================================
# 4. 继承设计最佳实践
# ============================================================================

class Shape:
    """
    形状基类 - 演示抽象基类的概念
    """
    
    def __init__(self, name):
        """
        构造函数
        
        Args:
            name (str): 形状名称
        """
        self.name = name
    
    def area(self):
        """
        计算面积 - 抽象方法，子类必须实现
        
        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("子类必须实现area方法")
    
    def perimeter(self):
        """
        计算周长 - 抽象方法，子类必须实现
        
        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("子类必须实现perimeter方法")
    
    def describe(self):
        """
        描述形状 - 通用方法
        """
        return f"这是一个{self.name}"
    
    def __str__(self):
        """字符串表示"""
        return f"{self.name}(面积:{self.area():.2f}, 周长:{self.perimeter():.2f})"


class Rectangle(Shape):
    """
    矩形类
    """
    
    def __init__(self, width, height):
        """
        构造函数
        
        Args:
            width (float): 宽度
            height (float): 高度
        """
        super().__init__("矩形")
        self.width = width
        self.height = height
    
    def area(self):
        """计算矩形面积"""
        return self.width * self.height
    
    def perimeter(self):
        """计算矩形周长"""
        return 2 * (self.width + self.height)
    
    def is_square(self):
        """
        判断是否为正方形
        
        Returns:
            bool: 是否为正方形
        """
        return abs(self.width - self.height) < 1e-10


class Circle(Shape):
    """
    圆形类
    """
    
    def __init__(self, radius):
        """
        构造函数
        
        Args:
            radius (float): 半径
        """
        super().__init__("圆形")
        self.radius = radius
    
    def area(self):
        """计算圆形面积"""
        import math
        return math.pi * self.radius ** 2
    
    def perimeter(self):
        """计算圆形周长"""
        import math
        return 2 * math.pi * self.radius
    
    def diameter(self):
        """
        计算直径
        
        Returns:
            float: 直径
        """
        return 2 * self.radius


class Triangle(Shape):
    """
    三角形类
    """
    
    def __init__(self, side_a, side_b, side_c):
        """
        构造函数
        
        Args:
            side_a (float): 边长a
            side_b (float): 边长b
            side_c (float): 边长c
        """
        super().__init__("三角形")
        
        # 验证三角形的有效性
        if not self._is_valid_triangle(side_a, side_b, side_c):
            raise ValueError("无效的三角形边长")
        
        self.side_a = side_a
        self.side_b = side_b
        self.side_c = side_c
    
    def _is_valid_triangle(self, a, b, c):
        """
        验证三角形的有效性
        
        Args:
            a, b, c (float): 三边长
            
        Returns:
            bool: 是否为有效三角形
        """
        return (a + b > c) and (a + c > b) and (b + c > a)
    
    def area(self):
        """使用海伦公式计算三角形面积"""
        s = self.perimeter() / 2  # 半周长
        import math
        return math.sqrt(s * (s - self.side_a) * (s - self.side_b) * (s - self.side_c))
    
    def perimeter(self):
        """计算三角形周长"""
        return self.side_a + self.side_b + self.side_c
    
    def triangle_type(self):
        """
        判断三角形类型
        
        Returns:
            str: 三角形类型
        """
        sides = sorted([self.side_a, self.side_b, self.side_c])
        
        if abs(sides[0] - sides[1]) < 1e-10 and abs(sides[1] - sides[2]) < 1e-10:
            return "等边三角形"
        elif abs(sides[0] - sides[1]) < 1e-10 or abs(sides[1] - sides[2]) < 1e-10:
            return "等腰三角形"
        else:
            return "普通三角形"


def demo_inheritance_best_practices():
    """演示继承设计的最佳实践"""
    print("=== 继承设计最佳实践 ===")
    
    # 创建不同形状的对象
    shapes = [
        Rectangle(5, 3),
        Circle(4),
        Triangle(3, 4, 5),
        Rectangle(4, 4)  # 正方形
    ]
    
    print("=== 多态性演示 ===")
    for shape in shapes:
        print(f"{shape.describe()}")
        print(f"  {shape}")
        
        # 特定类型的额外信息
        if isinstance(shape, Rectangle):
            if shape.is_square():
                print("  这是一个正方形")
        elif isinstance(shape, Triangle):
            print(f"  类型：{shape.triangle_type()}")
        elif isinstance(shape, Circle):
            print(f"  直径：{shape.diameter():.2f}")
        
        print()
    
    # 计算总面积
    total_area = sum(shape.area() for shape in shapes)
    print(f"所有形状的总面积：{total_area:.2f}")
    
    print()


# ============================================================================
# 主函数 - 运行所有示例
# ============================================================================

def main():
    """运行所有示例"""
    print("Python面向对象编程 - 继承示例")
    print("=" * 50)
    
    demo_basic_inheritance()
    demo_super_usage()
    demo_multiple_inheritance()
    demo_inheritance_best_practices()
    
    print("所有示例运行完成！")


if __name__ == "__main__":
    main()