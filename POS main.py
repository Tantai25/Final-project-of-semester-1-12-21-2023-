import pygame # Đây là thư viện mã nguồn mở trên ngôn ngữ Python dùng để lập trình video games. PyGame chứa đầy đủ các công cụ hỗ trợ lập trình game như đồ hoạt, hoạt hình, âm thanh, và sự kiện điều khiển.
from pygame import mixer # Module hiệu ứng âm thanh
import os #Module os trong python cho phép chúng ta làm việc với các tập tin và thư mục.
import random # Module random
import csv
import button

mixer.init()
pygame.init() # Để sử dụng các hàm của pygame , Chỉ cần biết khi dùng pygame thì nhớ thêm dòng này vào


SCREEN_WIDTH = 800 # Chiều dài của ửa sổ game
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8) # Chiều cao của ửa sổ game

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #Thiết lập các thông số chiều dài vầ cao trên
pygame.display.set_caption('POS') # Tên game

# Đặt tỷ lệ khung
clock = pygame.time.Clock()
FPS = 60

# Đặt các biến cho trò chơi
GRAVITY = 0.65   #trọng lực
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
end_game = False


# Xác định các biến hành động của người chơi
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False


# Tải nhạc và âm thanh cho nhân vật
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(2)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(2)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(2)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(2)


# Tải hình ảnh
# Các nút nhấn
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
# Nền
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
# Lưu trữ tiêu đề trong danh sách
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/Tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)
# Đạn
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
# Lựu đạn
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
#Hộp tiếp vũ khú
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
	'Health'	: health_box_img,
	'Ammo'		: ammo_box_img,
	'Grenade'	: grenade_box_img
}


# Màu sắc
BG = (28, 154, 161)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# Font chữ
font = pygame.font.SysFont('Futura', 30)
font2 = pygame.font.SysFont('Berlin Sans FB Demi',50)
font3 = pygame.font.SysFont('Berlin Sans FB Demi',40)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


def draw_bg():
	screen.fill(BG)
	width = sky_img.get_width()
	for x in range(5):
		screen.blit(pine2_img, ((x * width) - bg_scroll * 0.1, SCREEN_HEIGHT - pine2_img.get_height()))


# Hàm reset level
def reset_level():
	enemy_group.empty()
	bullet_group.empty()
	grenade_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	# Tạo danh sách ô trống
	data = []
	for row in range(ROWS):
		r = [-1] * COLS
		data.append(r)

	return data




class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_type = char_type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.health = 100
		self.max_health = self.health
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		# Các biến cụ thể của AI
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0
		
		# tải tất cả hình ảnh cho người chơi
		animation_types = ['Idle', 'Run', 'Jump', 'Death']
		for animation in animation_types:
			# Đặt lại danh sách hình ảnh tạm thời
			temp_list = []
			# Đếm số file trong thư mục
			num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()


	def update(self):
		self.update_animation()
		self.check_alive()
		# cập nhật thời gian hồi chiêu
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1


	def move(self, moving_left, moving_right):
		# thiết lập lại các biến chuyển động
		screen_scroll = 0
		dx = 0
		dy = 0

		# Gán các biến chuyển động nếu di chuyển sang trái hoặc phải
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		# Nhảy
		if self.jump == True and self.in_air == False:
			self.vel_y = -11
			self.jump = False
			self.in_air = True

		# Thiết lập trọng lực
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		# Kiểm tra các va chạm
		for tile in world.obstacle_list:
			# kiểm tra va chạm theo trục tọa độ x
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				# Nếu AI va vào tường thì bắt nó quay lại
				if self.char_type == 'enemy':
					self.direction *= -1
					self.move_counter = 0
			# kiểm tra va chạm theo trục tọa độ y
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				# Kiểm tra có ở dưỡi mặt đất hay không
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				# Kiểm tra có ở trên mặt đất không
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom


		# Kiểm tra va chạm với nước
		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0

		# Kiểm tra va chạm với lối ra
		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True

		# Kiểm tra xem có rơi ra khỏi bản đồ không
		if self.rect.bottom > SCREEN_HEIGHT:
			self.health = 0


		# Kiểm tra xem có bị lệch mép màn hình không
		if self.char_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
				dx = 0

		# Cập nhật vị trí hình chữ nhật
		self.rect.x += dx
		self.rect.y += dy

		# Màn hình cập nhật chạy theo người chơi
		if self.char_type == 'player':
			if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx

		return screen_scroll, level_complete



	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			# Xóa bớt đạn khi bắn
			self.ammo -= 1
			shot_fx.play()


	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)#0: Đứng yên
				self.idling = True
				self.idling_counter = 50
			# Kiểm tra AI có đứng gần người chơi
			if self.vision.colliderect(player.rect):
				# Đứng lại bắn người chơi
				self.update_action(0)#0: Đứng yên
				# Bắn
				self.shoot()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)#1: Chạy
					self.move_counter += 1
					# Cải tiến tầm nhìn bằng di chuyển nhân vật
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False

		#scroll
		self.rect.x += screen_scroll


	def update_animation(self):
		# Cập nhật nhân vật người chơi
		ANIMATION_COOLDOWN = 100
		# Cập nhật hình ảnh tùy thuộc vào khung hình hiện tại
		self.image = self.animation_list[self.action][self.frame_index]
		# Kiểm tra xem đã đủ thời gian trôi qua kể từ lần cập nhật cuối cùng chưa
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		# Nếu ảnh đã hết thì  thiết lập lại từ đầu
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0



	def update_action(self, new_action):
		# Kiểm tra xem hành động mới có khác với hành động trước không
		if new_action != self.action:
			self.action = new_action
			# Cập nhật cài đặt hoạt ảnh
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()



	def check_alive(self):
		# Kiểm tra còn sống hay không
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.level_length = len(data[0])
		# Lặp từng giá trị trong tệp dữ liệu cấp độ
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 15:# Tạo nhân vật người chơi
						player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16:# Tạo nhân vật đối thủ
						enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
						enemy_group.add(enemy)
					elif tile == 17:# Tạo hộp tiếp đạn
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 18:# Tạo hộp tiếp lựu đạn
						item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 19:# Tạo hộp tiếp máu
						item_box = ItemBox('Health', x * TILE_SIZE , y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 20:# Tạo nút thoát
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)
		return player, health_bar


	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll




class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


	def update(self):
		# Cuộn
		self.rect.x += screen_scroll
		# Kiểm tra xem người chơi đã nhặt được hộp chưa
		if pygame.sprite.collide_rect(self, player):
			# Kiểm tra xem nó là loại hộp gì
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 15
			elif self.item_type == 'Grenade':
				player.grenades += 3
			# Xóa các hộp nhận quà
			self.kill()


class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		# Cập nhật thanh máu
		self.health = health
		# Tính tỉ lệ máu còn lại
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		# Di chuyển viên đạn
		self.rect.x += (self.direction * self.speed) + screen_scroll
		# Kiểm tra xem viên đạn có biến mất khỏi màn hình không
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()
		# Kiểm tra va chạm với cấp độ
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		# Kiểm tra va chạm với nhân vật
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()



class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction

	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

		# Kiểm tra va chạm với cấp độ
		for tile in world.obstacle_list:
			# Kiểm tra va chạm với tường
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			# Kiểm tra va chạm theo hướng y
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				# kiểm tra xem có ở dưới mặt đất không, tức là bị rơi
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				# kiểm tra xem có ở trên mặt đất không, tức là nhảy quá cao
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom	


		# Cập nhật vị trí lựu đạn
		self.rect.x += dx + screen_scroll
		self.rect.y += dy

		# Đếm thời gian
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			grenade_fx.play()
			explosion = Explosion(self.rect.x, self.rect.y, 0.5)
			explosion_group.add(explosion)
			# Gây sát thương cho bất cứ ai ở gần
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health -= 50



class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0


	def update(self):
		# Cuộn
		self.rect.x += screen_scroll

		EXPLOSION_SPEED = 4
		# Cập nhật các hình ảnh cho vụ nổ
		self.counter += 1

		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			# Nếu nổ xong thì xóa vụ nổ
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]


class ScreenFade(): # Thiết lập chế độ làm mờ mà hình
	def __init__(self, direction, colour, speed):
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0

    # làm mờ màn hình
	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:# Mờ toàn bộ màn hình
			pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
			pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
		if self.direction == 2:# Màn hình dọc mờ dần
			pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
		if self.fade_counter >= SCREEN_WIDTH:
			fade_complete = True

		return fade_complete


# Tạo độ mờ màn hình
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)


# Tạo nút nhấn
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


# Tạo danh sách ô trống
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
# Tải các cấp độ và tạo thế giới
with open(f'level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)



run = True
while run:

	clock.tick(FPS)

	if start_game == False:
		# Tạo menu
		screen.fill(BG)
		draw_text('PURSUIT OF SCHOLARSHIP', font2, WHITE, 120, 90)
		# draw_text('100% FAILED ', font2, WHITE, 285, 300)
		# draw_text('=> $$ FOR SCHOOL', font2, WHITE, 260, 500)
		# Thêm các nút bắt đầu,...
		if start_button.draw(screen):
			start_game = True
			start_intro = True
		if exit_button.draw(screen):
			run = False
	else:
		# Cập nhật hình nền
		draw_bg()
		# Vẽ thế giới
		world.draw()
		# Vẽ thanh máu
		health_bar.draw(player.health)
		# Hiện số lượng đạn
		draw_text('AMMO: ', font, WHITE, 10, 35)
		for x in range(player.ammo):
			screen.blit(bullet_img, (90 + (x * 10), 40))
		# Hiện số lượng lựu đạn
		draw_text('PENCILS: ', font, WHITE, 10, 60)
		for x in range(player.grenades):
			screen.blit(grenade_img, (110 + (x * 27), 65))


		player.update()
		player.draw()

		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()

		# Cập nhật và vẽ các nhóm
		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		bullet_group.draw(screen)
		grenade_group.draw(screen)
		explosion_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)

		# Tạo intro
		if start_intro == True:
			if intro_fade.fade():
				start_intro = False
				intro_fade.fade_counter = 0


		# Cập nhật nhân vật người choi
		if player.alive:
			# Bắn đạn
			if shoot:
				player.shoot()
			# Ném lựu đạn
			elif grenade and grenade_thrown == False and player.grenades > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),player.rect.top, player.direction)
				grenade_group.add(grenade)
				# xóa lựu đạn khi ném
				player.grenades -= 1
				grenade_thrown = True
			if player.in_air:
				player.update_action(2)#2: Nhảy
			elif moving_left or moving_right:
				player.update_action(1)#1: Chạy
			else:
				player.update_action(0)#0:  Đứng yên
			screen_scroll, level_complete = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
			# Nếu người chơi xong màn thì chuyển sang màn tiếp theo
			if level_complete:
				start_intro = True
				level += 1
				bg_scroll = 0
				world_data = reset_level()
				# Tải các cấp dộ và tạo thế giới
				if level <= 3:
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)
				else:
					run = False
		else:
			screen_scroll = 0
			if death_fade.fade():
				draw_text('OH NO! ', font3, WHITE, 340, 110)
				draw_text(' GOOD LUCK FOR NEXT TIME!  ', font3, WHITE, 140, 170)
				if restart_button.draw(screen):
					death_fade.fade_counter = 0
					start_intro = True
					bg_scroll = 0
					world_data = reset_level()
					# Tải các cấp độ và tạo thế giới
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)

	for event in pygame.event.get():
		# Thoát game
		if event.type == pygame.QUIT:
			run = False
		# Các nút chức năng
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a: # Nút a để di chuyển sang trái
				moving_left = True
			if event.key == pygame.K_d: # Nút d để di chuyển sang phải
				moving_right = True
			if event.key == pygame.K_SPACE: # Nút SPACE để nhảy
				shoot = True
			if event.key == pygame.K_q: # Nút q để ném lựu đạn
				grenade = True
			if event.key == pygame.K_w and player.alive: # Nút w để nhảy
				player.jump = True
				jump_fx.play()
			if event.key == pygame.K_ESCAPE: # Nút Esc để thoát game
				run = False


		# Nút bàn phím được thả ra
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False
			if event.key == pygame.K_q:
				grenade = False
				grenade_thrown = False


	pygame.display.update()

pygame.quit() # Thoát game
