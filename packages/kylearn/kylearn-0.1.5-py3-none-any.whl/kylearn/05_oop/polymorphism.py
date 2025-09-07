"""
面向对象编程 - 多态示例

本模块演示Python中多态的概念和实现，包括：
1. 方法重写(Override)实现多态
2. 鸭子类型(Duck Typing)
3. 抽象基类(ABC)和接口设计
4. 多态在实际项目中的应用
5. 运算符重载
6. 多态设计模式
"""

from abc import ABC, abstractmethod
import math


# ============================================================================
# 1. 基本多态 - 方法重写
# ============================================================================

class Animal:
    """
    动物基类 - 演示基本多态概念
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
    
    def make_sound(self):
        """
        发出声音 - 基类提供默认实现
        """
        return f"{self.name}发出了声音"
    
    def move(self):
        """
        移动 - 基类提供默认实现
        """
        return f"{self.name}在移动"
    
    def eat(self, food):
        """
        吃东西 - 通用行为
        
        Args:
            food (str): 食物
        """
        return f"{self.name}正在吃{food}"
    
    def __str__(self):
        """字符串表示"""
        return f"{self.species}：{self.name}"


class Dog(Animal):
    """狗类 - 重写父类方法"""
    
    def __init__(self, name, breed):
        """
        构造函数
        
        Args:
            name (str): 狗的名字
            breed (str): 品种
        """
        super().__init__(name, "狗")
        self.breed = breed
    
    def make_sound(self):
        """重写：狗的叫声"""
        return f"{self.name}汪汪叫"
    
    def move(self):
        """重写：狗的移动方式"""
        return f"{self.name}在奔跑"
    
    def fetch(self, item):
        """狗特有的行为"""
        return f"{self.name}去捡{item}"


class Cat(Animal):
    """猫类 - 重写父类方法"""
    
    def __init__(self, name, color):
        """
        构造函数
        
        Args:
            name (str): 猫的名字
            color (str): 毛色
        """
        super().__init__(name, "猫")
        self.color = color
    
    def make_sound(self):
        """重写：猫的叫声"""
        return f"{self.name}喵喵叫"
    
    def move(self):
        """重写：猫的移动方式"""
        return f"{self.name}优雅地走动"
    
    def climb(self):
        """猫特有的行为"""
        return f"{self.name}爬到了高处"


class Bird(Animal):
    """鸟类 - 重写父类方法"""
    
    def __init__(self, name, wing_span):
        """
        构造函数
        
        Args:
            name (str): 鸟的名字
            wing_span (float): 翼展(米)
        """
        super().__init__(name, "鸟")
        self.wing_span = wing_span
    
    def make_sound(self):
        """重写：鸟的叫声"""
        return f"{self.name}啾啾叫"
    
    def move(self):
        """重写：鸟的移动方式"""
        return f"{self.name}在天空中飞翔"
    
    def fly_to(self, destination):
        """鸟特有的行为"""
        return f"{self.name}飞向{destination}"


def demo_basic_polymorphism():
    """演示基本多态概念"""
    print("=== 基本多态 - 方法重写 ===")
    
    # 创建不同类型的动物
    animals = [
        Dog("旺财", "金毛"),
        Cat("咪咪", "橘色"),
        Bird("小鸟", 0.3),
        Animal("通用动物", "未知")
    ]
    
    print("=== 多态行为演示 ===")
    for animal in animals:
        print(f"\n{animal}")
        print(f"  叫声：{animal.make_sound()}")
        print(f"  移动：{animal.move()}")
        print(f"  吃东西：{animal.eat('食物')}")
    
    # 演示多态的威力 - 统一接口处理不同对象
    print(f"\n=== 统一接口处理 ===")
    
    def animal_concert(animal_list):
        """动物音乐会 - 统一调用make_sound方法"""
        print("🎵 动物音乐会开始！")
        for animal in animal_list:
            print(f"  {animal.make_sound()}")
        print("🎵 音乐会结束！")
    
    def animal_race(animal_list):
        """动物赛跑 - 统一调用move方法"""
        print("🏃 动物赛跑开始！")
        for animal in animal_list:
            print(f"  {animal.move()}")
        print("🏃 赛跑结束！")
    
    animal_concert(animals)
    print()
    animal_race(animals)
    
    print()


# ============================================================================
# 2. 鸭子类型(Duck Typing)
# ============================================================================

class Duck:
    """鸭子类"""
    
    def __init__(self, name):
        self.name = name
    
    def quack(self):
        """鸭子叫"""
        return f"{self.name}嘎嘎叫"
    
    def fly(self):
        """鸭子飞"""
        return f"{self.name}扑腾着翅膀飞行"


class Robot:
    """机器人类 - 不继承Duck但有相同的方法"""
    
    def __init__(self, model):
        self.model = model
    
    def quack(self):
        """机器人模拟鸭子叫"""
        return f"机器人{self.model}发出电子嘎嘎声"
    
    def fly(self):
        """机器人飞行"""
        return f"机器人{self.model}启动推进器飞行"


class Person:
    """人类 - 可以模拟鸭子行为"""
    
    def __init__(self, name):
        self.name = name
    
    def quack(self):
        """人模拟鸭子叫"""
        return f"{self.name}学鸭子叫：嘎嘎嘎"
    
    def fly(self):
        """人类"飞行"(想象中)"""
        return f"{self.name}张开双臂假装飞行"


class Airplane:
    """飞机类 - 只有fly方法"""
    
    def __init__(self, model):
        self.model = model
    
    def fly(self):
        """飞机飞行"""
        return f"{self.model}飞机在高空飞行"
    
    # 注意：飞机没有quack方法


def demo_duck_typing():
    """演示鸭子类型"""
    print("=== 鸭子类型(Duck Typing) ===")
    
    # 创建不同类型的对象
    duck = Duck("唐老鸭")
    robot = Robot("R2D2")
    person = Person("小明")
    airplane = Airplane("波音747")
    
    # 鸭子类型函数 - 如果对象有相应方法就可以调用
    def make_it_quack(obj):
        """让对象叫 - 鸭子类型"""
        try:
            return obj.quack()
        except AttributeError:
            return f"{obj}不会叫"
    
    def make_it_fly(obj):
        """让对象飞 - 鸭子类型"""
        try:
            return obj.fly()
        except AttributeError:
            return f"{obj}不会飞"
    
    def duck_behavior(obj):
        """完整的鸭子行为 - 需要同时有quack和fly方法"""
        try:
            quack_result = obj.quack()
            fly_result = obj.fly()
            return f"鸭子行为：{quack_result}，{fly_result}"
        except AttributeError as e:
            return f"不是完整的鸭子：缺少方法 {e}"
    
    objects = [duck, robot, person, airplane]
    
    print("=== 测试叫声 ===")
    for obj in objects:
        print(f"  {make_it_quack(obj)}")
    
    print(f"\n=== 测试飞行 ===")
    for obj in objects:
        print(f"  {make_it_fly(obj)}")
    
    print(f"\n=== 测试完整鸭子行为 ===")
    for obj in objects:
        print(f"  {duck_behavior(obj)}")
    
    # 更高级的鸭子类型检查
    def is_duck_like(obj):
        """检查对象是否像鸭子"""
        return hasattr(obj, 'quack') and hasattr(obj, 'fly')
    
    print(f"\n=== 鸭子类型检查 ===")
    for obj in objects:
        duck_like = is_duck_like(obj)
        obj_name = getattr(obj, 'name', getattr(obj, 'model', str(obj)))
        print(f"  {obj_name}像鸭子吗？{duck_like}")
    
    print()


# ============================================================================
# 3. 抽象基类(ABC)和接口设计
# ============================================================================

class Shape(ABC):
    """
    形状抽象基类 - 定义接口
    """
    
    def __init__(self, name):
        """
        构造函数
        
        Args:
            name (str): 形状名称
        """
        self.name = name
    
    @abstractmethod
    def area(self):
        """
        计算面积 - 抽象方法，子类必须实现
        
        Returns:
            float: 面积
        """
        pass
    
    @abstractmethod
    def perimeter(self):
        """
        计算周长 - 抽象方法，子类必须实现
        
        Returns:
            float: 周长
        """
        pass
    
    def describe(self):
        """
        描述形状 - 具体方法，子类可以重写
        
        Returns:
            str: 形状描述
        """
        return f"这是一个{self.name}，面积为{self.area():.2f}，周长为{self.perimeter():.2f}"
    
    def __str__(self):
        """字符串表示"""
        return f"{self.name}(面积:{self.area():.2f})"


class Rectangle(Shape):
    """矩形类 - 实现抽象基类"""
    
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
        """实现抽象方法：计算矩形面积"""
        return self.width * self.height
    
    def perimeter(self):
        """实现抽象方法：计算矩形周长"""
        return 2 * (self.width + self.height)
    
    def is_square(self):
        """矩形特有方法：判断是否为正方形"""
        return abs(self.width - self.height) < 1e-10


class Circle(Shape):
    """圆形类 - 实现抽象基类"""
    
    def __init__(self, radius):
        """
        构造函数
        
        Args:
            radius (float): 半径
        """
        super().__init__("圆形")
        self.radius = radius
    
    def area(self):
        """实现抽象方法：计算圆形面积"""
        return math.pi * self.radius ** 2
    
    def perimeter(self):
        """实现抽象方法：计算圆形周长"""
        return 2 * math.pi * self.radius
    
    def diameter(self):
        """圆形特有方法：计算直径"""
        return 2 * self.radius


class Triangle(Shape):
    """三角形类 - 实现抽象基类"""
    
    def __init__(self, side_a, side_b, side_c):
        """
        构造函数
        
        Args:
            side_a (float): 边长a
            side_b (float): 边长b  
            side_c (float): 边长c
        """
        super().__init__("三角形")
        
        # 验证三角形有效性
        if not self._is_valid_triangle(side_a, side_b, side_c):
            raise ValueError("无效的三角形边长")
        
        self.side_a = side_a
        self.side_b = side_b
        self.side_c = side_c
    
    def _is_valid_triangle(self, a, b, c):
        """验证三角形有效性"""
        return (a + b > c) and (a + c > b) and (b + c > a)
    
    def area(self):
        """实现抽象方法：使用海伦公式计算三角形面积"""
        s = self.perimeter() / 2
        return math.sqrt(s * (s - self.side_a) * (s - self.side_b) * (s - self.side_c))
    
    def perimeter(self):
        """实现抽象方法：计算三角形周长"""
        return self.side_a + self.side_b + self.side_c
    
    def triangle_type(self):
        """三角形特有方法：判断三角形类型"""
        sides = sorted([self.side_a, self.side_b, self.side_c])
        
        if abs(sides[0] - sides[1]) < 1e-10 and abs(sides[1] - sides[2]) < 1e-10:
            return "等边三角形"
        elif abs(sides[0] - sides[1]) < 1e-10 or abs(sides[1] - sides[2]) < 1e-10:
            return "等腰三角形"
        else:
            return "普通三角形"


def demo_abstract_base_class():
    """演示抽象基类"""
    print("=== 抽象基类(ABC)和接口设计 ===")
    
    # 创建不同形状的对象
    shapes = [
        Rectangle(5, 3),
        Circle(4),
        Triangle(3, 4, 5),
        Rectangle(6, 6)  # 正方形
    ]
    
    print("=== 多态处理不同形状 ===")
    for shape in shapes:
        print(f"{shape.describe()}")
        
        # 根据具体类型调用特有方法
        if isinstance(shape, Rectangle):
            if shape.is_square():
                print("  这是一个正方形")
        elif isinstance(shape, Circle):
            print(f"  直径：{shape.diameter():.2f}")
        elif isinstance(shape, Triangle):
            print(f"  类型：{shape.triangle_type()}")
        
        print()
    
    # 统一处理 - 多态的威力
    def calculate_total_area(shape_list):
        """计算总面积 - 多态函数"""
        total = sum(shape.area() for shape in shape_list)
        return total
    
    def find_largest_shape(shape_list):
        """找到面积最大的形状 - 多态函数"""
        return max(shape_list, key=lambda s: s.area())
    
    total_area = calculate_total_area(shapes)
    largest_shape = find_largest_shape(shapes)
    
    print(f"=== 统计信息 ===")
    print(f"总面积：{total_area:.2f}")
    print(f"最大形状：{largest_shape}")
    
    # 尝试创建抽象基类实例(会失败)
    print(f"\n=== 尝试创建抽象基类实例 ===")
    try:
        abstract_shape = Shape("抽象形状")
    except TypeError as e:
        print(f"无法创建抽象基类实例：{e}")
    
    print()


# ============================================================================
# 4. 运算符重载实现多态
# ============================================================================

class Vector:
    """
    向量类 - 演示运算符重载
    """
    
    def __init__(self, x, y):
        """
        构造函数
        
        Args:
            x (float): x坐标
            y (float): y坐标
        """
        self.x = x
        self.y = y
    
    def __add__(self, other):
        """
        加法运算符重载
        
        Args:
            other (Vector): 另一个向量
            
        Returns:
            Vector: 向量和
        """
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        return NotImplemented
    
    def __sub__(self, other):
        """
        减法运算符重载
        
        Args:
            other (Vector): 另一个向量
            
        Returns:
            Vector: 向量差
        """
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        return NotImplemented
    
    def __mul__(self, scalar):
        """
        乘法运算符重载(标量乘法)
        
        Args:
            scalar (float): 标量
            
        Returns:
            Vector: 缩放后的向量
        """
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        return NotImplemented
    
    def __rmul__(self, scalar):
        """右乘法运算符重载"""
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        """
        除法运算符重载
        
        Args:
            scalar (float): 标量
            
        Returns:
            Vector: 缩放后的向量
        """
        if isinstance(scalar, (int, float)) and scalar != 0:
            return Vector(self.x / scalar, self.y / scalar)
        return NotImplemented
    
    def __eq__(self, other):
        """
        相等比较运算符重载
        
        Args:
            other (Vector): 另一个向量
            
        Returns:
            bool: 是否相等
        """
        if isinstance(other, Vector):
            return abs(self.x - other.x) < 1e-10 and abs(self.y - other.y) < 1e-10
        return False
    
    def __lt__(self, other):
        """
        小于比较运算符重载(按模长比较)
        
        Args:
            other (Vector): 另一个向量
            
        Returns:
            bool: 是否小于
        """
        if isinstance(other, Vector):
            return self.magnitude() < other.magnitude()
        return NotImplemented
    
    def __abs__(self):
        """
        绝对值运算符重载(返回模长)
        
        Returns:
            float: 向量模长
        """
        return self.magnitude()
    
    def __neg__(self):
        """
        负号运算符重载
        
        Returns:
            Vector: 相反向量
        """
        return Vector(-self.x, -self.y)
    
    def __str__(self):
        """字符串表示"""
        return f"Vector({self.x:.2f}, {self.y:.2f})"
    
    def __repr__(self):
        """官方字符串表示"""
        return f"Vector({self.x}, {self.y})"
    
    def magnitude(self):
        """
        计算向量模长
        
        Returns:
            float: 模长
        """
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def dot_product(self, other):
        """
        计算点积
        
        Args:
            other (Vector): 另一个向量
            
        Returns:
            float: 点积
        """
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        raise TypeError("点积运算需要Vector对象")
    
    def normalize(self):
        """
        归一化向量
        
        Returns:
            Vector: 单位向量
        """
        mag = self.magnitude()
        if mag == 0:
            return Vector(0, 0)
        return Vector(self.x / mag, self.y / mag)


def demo_operator_overloading():
    """演示运算符重载"""
    print("=== 运算符重载实现多态 ===")
    
    # 创建向量
    v1 = Vector(3, 4)
    v2 = Vector(1, 2)
    v3 = Vector(3, 4)
    
    print(f"向量v1：{v1}")
    print(f"向量v2：{v2}")
    print(f"向量v3：{v3}")
    
    # 算术运算
    print(f"\n=== 算术运算 ===")
    print(f"v1 + v2 = {v1 + v2}")
    print(f"v1 - v2 = {v1 - v2}")
    print(f"v1 * 2 = {v1 * 2}")
    print(f"3 * v1 = {3 * v1}")
    print(f"v1 / 2 = {v1 / 2}")
    
    # 比较运算
    print(f"\n=== 比较运算 ===")
    print(f"v1 == v2: {v1 == v2}")
    print(f"v1 == v3: {v1 == v3}")
    print(f"v1 < v2: {v1 < v2}")
    print(f"v2 < v1: {v2 < v1}")
    
    # 一元运算
    print(f"\n=== 一元运算 ===")
    print(f"-v1 = {-v1}")
    print(f"abs(v1) = {abs(v1):.2f}")
    print(f"v1的模长：{v1.magnitude():.2f}")
    
    # 向量运算
    print(f"\n=== 向量运算 ===")
    print(f"v1 · v2 = {v1.dot_product(v2):.2f}")
    print(f"v1归一化：{v1.normalize()}")
    
    # 链式运算
    print(f"\n=== 链式运算 ===")
    result = (v1 + v2) * 2 - v3
    print(f"(v1 + v2) * 2 - v3 = {result}")
    
    # 多态性 - 不同类型的向量运算
    class Vector3D(Vector):
        """3D向量类 - 扩展2D向量"""
        
        def __init__(self, x, y, z):
            super().__init__(x, y)
            self.z = z
        
        def __add__(self, other):
            if isinstance(other, Vector3D):
                return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
            elif isinstance(other, Vector):
                return Vector3D(self.x + other.x, self.y + other.y, self.z)
            return NotImplemented
        
        def magnitude(self):
            return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        
        def __str__(self):
            return f"Vector3D({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
    
    v3d = Vector3D(1, 2, 3)
    print(f"\n=== 3D向量多态 ===")
    print(f"3D向量：{v3d}")
    print(f"3D向量模长：{v3d.magnitude():.2f}")
    print(f"2D + 3D：{v1 + v3d}")  # 多态运算
    
    print()


# ============================================================================
# 5. 实际应用 - 图形绘制系统
# ============================================================================

class Drawable(ABC):
    """
    可绘制对象抽象基类
    """
    
    @abstractmethod
    def draw(self):
        """
        绘制方法 - 抽象方法
        """
        pass
    
    @abstractmethod
    def get_bounds(self):
        """
        获取边界 - 抽象方法
        
        Returns:
            tuple: (x, y, width, height)
        """
        pass


class GraphicShape(Drawable):
    """
    图形形状基类
    """
    
    def __init__(self, x, y, color="black"):
        """
        构造函数
        
        Args:
            x (float): x坐标
            y (float): y坐标
            color (str): 颜色
        """
        self.x = x
        self.y = y
        self.color = color
    
    def move(self, dx, dy):
        """
        移动图形
        
        Args:
            dx (float): x方向偏移
            dy (float): y方向偏移
        """
        self.x += dx
        self.y += dy
    
    def set_color(self, color):
        """
        设置颜色
        
        Args:
            color (str): 颜色
        """
        self.color = color


class GraphicRectangle(GraphicShape):
    """图形矩形类"""
    
    def __init__(self, x, y, width, height, color="black"):
        """
        构造函数
        
        Args:
            x (float): x坐标
            y (float): y坐标
            width (float): 宽度
            height (float): 高度
            color (str): 颜色
        """
        super().__init__(x, y, color)
        self.width = width
        self.height = height
    
    def draw(self):
        """绘制矩形"""
        return f"绘制{self.color}矩形：位置({self.x}, {self.y})，大小{self.width}x{self.height}"
    
    def get_bounds(self):
        """获取矩形边界"""
        return (self.x, self.y, self.width, self.height)


class GraphicCircle(GraphicShape):
    """图形圆形类"""
    
    def __init__(self, x, y, radius, color="black"):
        """
        构造函数
        
        Args:
            x (float): 圆心x坐标
            y (float): 圆心y坐标
            radius (float): 半径
            color (str): 颜色
        """
        super().__init__(x, y, color)
        self.radius = radius
    
    def draw(self):
        """绘制圆形"""
        return f"绘制{self.color}圆形：圆心({self.x}, {self.y})，半径{self.radius}"
    
    def get_bounds(self):
        """获取圆形边界"""
        return (self.x - self.radius, self.y - self.radius, 
                2 * self.radius, 2 * self.radius)


class Text(Drawable):
    """文本类"""
    
    def __init__(self, x, y, text, font_size=12, color="black"):
        """
        构造函数
        
        Args:
            x (float): x坐标
            y (float): y坐标
            text (str): 文本内容
            font_size (int): 字体大小
            color (str): 颜色
        """
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size
        self.color = color
    
    def draw(self):
        """绘制文本"""
        return f"绘制{self.color}文本：'{self.text}'，位置({self.x}, {self.y})，字体大小{self.font_size}"
    
    def get_bounds(self):
        """获取文本边界(简化计算)"""
        width = len(self.text) * self.font_size * 0.6  # 简化的宽度计算
        height = self.font_size
        return (self.x, self.y, width, height)


class Canvas:
    """画布类 - 使用多态管理不同类型的图形对象"""
    
    def __init__(self, width, height):
        """
        构造函数
        
        Args:
            width (float): 画布宽度
            height (float): 画布高度
        """
        self.width = width
        self.height = height
        self.objects = []  # 存储所有可绘制对象
    
    def add_object(self, obj):
        """
        添加对象到画布
        
        Args:
            obj (Drawable): 可绘制对象
        """
        if isinstance(obj, Drawable):
            self.objects.append(obj)
            print(f"添加对象到画布：{type(obj).__name__}")
        else:
            raise TypeError("对象必须实现Drawable接口")
    
    def remove_object(self, obj):
        """
        从画布移除对象
        
        Args:
            obj (Drawable): 要移除的对象
        """
        if obj in self.objects:
            self.objects.remove(obj)
            print(f"从画布移除对象：{type(obj).__name__}")
    
    def draw_all(self):
        """绘制所有对象 - 多态方法调用"""
        print(f"开始绘制画布({self.width}x{self.height})：")
        for i, obj in enumerate(self.objects, 1):
            print(f"  {i}. {obj.draw()}")
        print("绘制完成")
    
    def get_total_bounds(self):
        """
        获取所有对象的总边界
        
        Returns:
            tuple: (min_x, min_y, max_x, max_y)
        """
        if not self.objects:
            return (0, 0, 0, 0)
        
        bounds_list = [obj.get_bounds() for obj in self.objects]
        
        min_x = min(bounds[0] for bounds in bounds_list)
        min_y = min(bounds[1] for bounds in bounds_list)
        max_x = max(bounds[0] + bounds[2] for bounds in bounds_list)
        max_y = max(bounds[1] + bounds[3] for bounds in bounds_list)
        
        return (min_x, min_y, max_x, max_y)
    
    def find_objects_at_point(self, x, y):
        """
        查找指定点的对象
        
        Args:
            x (float): x坐标
            y (float): y坐标
            
        Returns:
            list: 包含该点的对象列表
        """
        result = []
        for obj in self.objects:
            bounds = obj.get_bounds()
            if (bounds[0] <= x <= bounds[0] + bounds[2] and 
                bounds[1] <= y <= bounds[1] + bounds[3]):
                result.append(obj)
        return result
    
    def get_statistics(self):
        """
        获取画布统计信息
        
        Returns:
            dict: 统计信息
        """
        type_counts = {}
        for obj in self.objects:
            obj_type = type(obj).__name__
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        
        return {
            "total_objects": len(self.objects),
            "type_counts": type_counts,
            "bounds": self.get_total_bounds()
        }


def demo_graphics_system():
    """演示图形绘制系统"""
    print("=== 实际应用 - 图形绘制系统 ===")
    
    # 创建画布
    canvas = Canvas(800, 600)
    
    # 创建不同类型的图形对象
    rect1 = GraphicRectangle(10, 10, 100, 50, "红色")
    rect2 = GraphicRectangle(150, 30, 80, 80, "蓝色")
    circle1 = GraphicCircle(300, 100, 40, "绿色")
    circle2 = GraphicCircle(400, 150, 30, "黄色")
    text1 = Text(50, 200, "Hello World!", 16, "黑色")
    text2 = Text(200, 250, "Python多态示例", 14, "紫色")
    
    # 添加对象到画布
    print("=== 添加对象到画布 ===")
    objects = [rect1, rect2, circle1, circle2, text1, text2]
    for obj in objects:
        canvas.add_object(obj)
    
    # 绘制所有对象 - 多态调用
    print(f"\n=== 绘制画布 ===")
    canvas.draw_all()
    
    # 移动一些对象
    print(f"\n=== 移动对象 ===")
    rect1.move(20, 30)
    circle1.move(-50, 20)
    print("移动了矩形1和圆形1")
    
    # 重新绘制
    print(f"\n=== 重新绘制 ===")
    canvas.draw_all()
    
    # 查找指定点的对象
    print(f"\n=== 查找对象 ===")
    point_x, point_y = 100, 100
    objects_at_point = canvas.find_objects_at_point(point_x, point_y)
    print(f"坐标({point_x}, {point_y})处的对象：")
    for obj in objects_at_point:
        print(f"  {type(obj).__name__}: {obj.draw()}")
    
    # 获取统计信息
    print(f"\n=== 画布统计 ===")
    stats = canvas.get_statistics()
    print(f"总对象数：{stats['total_objects']}")
    print(f"对象类型统计：{stats['type_counts']}")
    print(f"总边界：{stats['bounds']}")
    
    # 演示多态的威力 - 统一处理不同类型的对象
    def batch_operation(drawable_objects, operation):
        """批量操作 - 多态函数"""
        results = []
        for obj in drawable_objects:
            if operation == "draw":
                results.append(obj.draw())
            elif operation == "bounds":
                results.append(obj.get_bounds())
        return results
    
    print(f"\n=== 批量操作演示 ===")
    all_drawings = batch_operation(canvas.objects, "draw")
    print("所有对象的绘制信息：")
    for i, drawing in enumerate(all_drawings, 1):
        print(f"  {i}. {drawing}")
    
    print()


# ============================================================================
# 主函数 - 运行所有示例
# ============================================================================

def main():
    """运行所有示例"""
    print("Python面向对象编程 - 多态示例")
    print("=" * 50)
    
    demo_basic_polymorphism()
    demo_duck_typing()
    demo_abstract_base_class()
    demo_operator_overloading()
    demo_graphics_system()
    
    print("所有示例运行完成！")


if __name__ == "__main__":
    main()