import random
import pyautogui
import image
import cv2


# 鼠标左键点击
def click(x, y):
    if pyautogui.onScreen(x, y):
        pyautogui.click(x, y, duration=0.1)


# RGB转BGR
def rgb_to_bgr(rgb):
    return rgb[2], rgb[1], rgb[0]


# 数组比较
def equal(arr1, arr2):
    if arr1[0] == arr2[0] and arr1[1] == arr2[1] and arr1[2] == arr2[2]:
        return True
    return False


class BoomMine:
    __inited = False
    blocks_x, blocks_y = -1, -1
    width, height = -1, -1
    img_cv, img = -1, -1
    blocks_img = [[-1 for i in range(blocks_y)] for i in range(blocks_x)]
    blocks_num = [[-3 for i in range(blocks_y)] for i in range(blocks_x)]
    blocks_is_mine = [[0 for i in range(blocks_y)] for i in range(blocks_x)]

    is_new_start = True

    next_steps = []

    # 遍历方块图像
    def iterate_blocks_image(self, func):
        if self.__inited:
            for y in range(self.blocks_y):
                for x in range(self.blocks_x):
                    # args are: self, [0]singleBlockImage, [1]location(as an array)
                    func(self, self.blocks_img[x][y], (x, y))

    # 遍历方块内容
    def iterate_blocks_number(self, func):
        if self.__inited:
            for y in range(self.blocks_y):
                for x in range(self.blocks_x):
                    # args are: self, [0]singleBlockNumber, [1]location(as an array)
                    func(self, (x, y))

    def analyze_block(self, block, location):
        """
        :param block: img, image of a single block
        :param location: location of a single block
        :return: blocks_num[location[0]][location[1]]
        """

        x, y = location[0], location[1]
        now_num = self.blocks_num[x][y]

        #  0:Flag
        #  9:Mine
        # -1:Not opened
        # -2:Opened but blank
        # -3:Uninitialized

        if not now_num == -2 and not 0 < now_num < 9:

            block = image.pil_to_cv(block)
            block_color = block[12, 12]  # center

            # Opened
            if equal(block_color, rgb_to_bgr((192, 192, 192))):
                if equal(block[1, 2], rgb_to_bgr((255, 255, 255))):
                    self.blocks_num[x][y] = -1
                elif equal(block[6][6], rgb_to_bgr((0, 0, 0))):
                    self.blocks_num[x][y] = 7
                else:
                    self.blocks_num[x][y] = -2
                    self.is_started = True

            elif equal(block_color, rgb_to_bgr((0, 0, 255))):
                self.blocks_num[x][y] = 1

            elif equal(block[16][8], rgb_to_bgr((0, 128, 0))):
                self.blocks_num[x][y] = 2

            elif equal(block[5][5], rgb_to_bgr((255, 0, 0))):
                self.blocks_num[x][y] = 3

            elif equal(block[16][16], rgb_to_bgr((0, 0, 128))):
                self.blocks_num[x][y] = 4

            elif equal(block[5][5], rgb_to_bgr((128, 0, 0))):
                self.blocks_num[x][y] = 5

            elif equal(block_color, rgb_to_bgr((0, 128, 128))):
                self.blocks_num[x][y] = 6

            elif equal(block[8][8], rgb_to_bgr((255, 0, 0))):
                # Is flag
                self.blocks_num[x][y] = 0

            elif equal(block_color, rgb_to_bgr((0, 0, 0))):
                if equal(block[10, 10], rgb_to_bgr((255, 255, 255))):
                    # Is mine
                    self.blocks_num[x][y] = 9

            elif equal(block_color, rgb_to_bgr((128, 128, 128))):
                self.blocks_num[x][y] = 8
            else:
                self.blocks_num[x][y] = -3
                self.is_mine_formed = False

    def detect_mine(self, location):
        """
        :param location: (x, y), location of a single block
        :return: block_is_mine:array, 0:not mine, 1:mine
        """

        def generate_kernel(k, k_width, k_height, block_location):
            """
            :param k:array, 0:not to visit, 1: to visit
            :param k_width:
            :param k_height:
            :param block_location: (x, y), location of a single block
            :return: lst:list, to visit map
            """
            lst = []
            loc_x, loc_y = block_location[0], block_location[1]
            for now_y in range(k_height):
                for now_x in range(k_width):

                    if k[now_y][now_x]:
                        rel_x, rel_y = now_x - 1, now_y - 1
                        lst.append((loc_y + rel_y, loc_x + rel_x))
            return lst

        def count_unopened_blocks(blocks):
            """
            :param blocks: list, list of blocks to visit
            :return: count, the number of the unopened blocks in the blocks list
            """
            count = 0
            for single_block in blocks:
                if self.blocks_num[single_block[1]][single_block[0]] == -1:
                    count += 1
            return count

        def mark_as_mine(blocks):
            """
            :param blocks: list, list of blocks which are mine
            :return: block_is mine: array, 0:not mine, 1:mine
            """
            for single_block in blocks:
                if self.blocks_num[single_block[1]][single_block[0]] == -1:
                    self.blocks_is_mine[single_block[1]][single_block[0]] = 1

        x, y = location[0], location[1]
        block = self.blocks_num[x][y]
        # 边界上的block所在的九宫格不完整，需要排除超限的坐标
        if 0 < self.blocks_num[x][y] < 9:

            kernel_width, kernel_height = 3, 3

            # Kernel mode:[Row][Col]
            kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

            # Left border
            if x == 0:
                for i in range(kernel_height):
                    kernel[i][0] = 0

            # Right border
            if x == self.blocks_x - 1:
                for i in range(kernel_height):
                    kernel[i][kernel_width - 1] = 0

            # Top border
            if y == 0:
                for i in range(kernel_width):
                    kernel[0][i] = 0

            # Bottom border
            if y == self.blocks_y - 1:
                for i in range(kernel_width):
                    kernel[kernel_height - 1][i] = 0

            # Generate to visit map
            to_visit = generate_kernel(kernel, kernel_width, kernel_height, location)

            unopened_blocks = count_unopened_blocks(to_visit)
            if unopened_blocks == block:
                mark_as_mine(to_visit)

    def detect_to_click_block(self, block, location):
        """
        :param block: int, the num of a single block in blocks_num
        :param location: (x, y), location of a single block
        :return: next_steps: list, the list of the location of the blocks to click
        """

        def generate_kernel(k, k_width, k_height, block_location):
            """
            :param k:array
            :param k_width:
            :param k_height:
            :param block_location: (x, y), location of a single block
            :return: lst:list, to visit map
            """
            lst = []
            loc_x, loc_y = block_location[0], block_location[1]
            for now_y in range(k_height):
                for now_x in range(k_width):

                    if k[now_y][now_x]:
                        rel_x, rel_y = now_x - 1, now_y - 1
                        lst.append((loc_y + rel_y, loc_x + rel_x))
            return lst

        def count_mines(blocks):
            """
            :param blocks: list, list of blocks to visit
            :return: count, the number of blocks which are mine in the blocks list
            """
            count = 0
            for single_block in blocks:
                if self.blocks_is_mine[single_block[1]][single_block[0]] == 1:
                    count += 1
            return count

        def mark_to_click_block(blocks):
            """
            :param blocks: list, list of blocks to visit
            :return: next_steps: list, the list of the location of the blocks to click
            """
            for single_block in blocks:

                # Not Mine
                if not self.blocks_is_mine[single_block[1]][single_block[0]] == 1:

                    # unopened
                    if self.blocks_num[single_block[1]][single_block[0]] == -1:

                        # Source Syntax: [y][x] - Converted
                        if not (single_block[1], single_block[0]) in self.next_steps:
                            self.next_steps.append((single_block[1], single_block[0]))

        x, y = location[0], location[1]

        if block > 0:

            kernel_width, kernel_height = 3, 3

            # Kernel mode:[Row][Col]
            kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

            # Left border
            if x == 0:
                for i in range(kernel_height):
                    kernel[i][0] = 0

            # Right border
            if x == self.blocks_x - 1:
                for i in range(kernel_height):
                    kernel[i][kernel_width - 1] = 0

            # Top border
            if y == 0:
                for i in range(kernel_width):
                    kernel[0][i] = 0

            # Bottom border
            if y == self.blocks_y - 1:
                for i in range(kernel_width):
                    kernel[kernel_height - 1][i] = 0

            # Generate to visit map
            to_visit = generate_kernel(kernel, kernel_width, kernel_height, location)

            mines_count = count_mines(to_visit)

            if mines_count == block:
                mark_to_click_block(to_visit)

    # block's relative location -> real location
    def rel_loc_to_real(self, block_rel_location):
        return self.left + 24 * block_rel_location[0] + 12, self.top + 24 * block_rel_location[1] + 12

    # Initialize
    def __init__(self):
        self.next_steps = []
        self.left = 0
        self.top = 0
        self.right = 0
        self.bottom = 0
        self.continue_random_click = False
        self.is_mine_formed = True
        self.is_started = False
        self.have_solved = False
        if self.process_once():
            self.__inited = True

    def process_once(self):

        result = image.get_frame()

        self.img, self.blocks_img, form_size, img_size, form_location = result

        self.blocks_num = [[-1 for i in range(self.blocks_y)] for i in range(self.blocks_x)]
        self.blocks_is_mine = [[0 for i in range(self.blocks_y)] for i in range(self.blocks_x)]
        self.next_steps = []
        self.is_new_start = True
        self.is_mine_formed = True

        self.blocks_x, self.blocks_y = form_size[0], form_size[1]
        self.width, self.height = img_size[0], img_size[1]
        self.img_cv = image.pil_to_cv(self.img)
        self.left, self.top, self.right, self.bottom = form_location

        # Analyze the blocks
        self.iterate_blocks_image(BoomMine.analyze_block)

        # Mark all mines
        self.iterate_blocks_number(BoomMine.detect_mine)

        # Calculate where to click
        self.iterate_blocks_number(BoomMine.detect_to_click_block)

        self.have_solved = False
        if len(self.next_steps) > 0:
            self.have_solved = True

            for to_click in self.next_steps:
                on_screen_location = self.rel_loc_to_real(to_click)
                click(on_screen_location[0], on_screen_location[1])

        if not self.have_solved and self.is_mine_formed:

            rand_location = (random.randint(0, self.blocks_x - 1), random.randint(0, self.blocks_y - 1))
            rand_x, rand_y = rand_location[0], rand_location[1]
            iter_times = 0

            if len(self.blocks_is_mine) > 0:

                while self.blocks_is_mine[rand_x][rand_y] or not self.blocks_num[rand_x][
                                                                     rand_y] == -1 and iter_times < 50:
                    rand_location = (random.randint(0, self.blocks_x - 1), random.randint(0, self.blocks_y - 1))
                    rand_x, rand_y = rand_location[0], rand_location[1]
                    iter_times += 1

            screen_location = self.rel_loc_to_real((rand_location[0], rand_location[1]))
            click(screen_location[0], screen_location[1])

        cv2.imshow("Sweeper Screenshot", self.img_cv)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
        return True


miner = BoomMine()

while 1:
    try:
        miner.process_once()
    except:
        pass
