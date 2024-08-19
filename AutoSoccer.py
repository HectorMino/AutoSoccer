import pygame, sys, threading, random, math, time
from screeninfo import get_monitors


monitor = get_monitors()

screen_width = 1600
screen_height = 900
#screen_width = monitor[0].width
#screen_height = monitor[0].height

half_height = screen_height / 2
half_width = screen_width / 2
line_color = (255, 0, 0, 128) 

line_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (54, 128, 45)

player_size = [(screen_width * screen_height * 50) / 2073600, (screen_width * screen_height * 50) / 2073600]
ball_size = [(screen_width * screen_height * 40) / 2073600, (screen_width * screen_height * 35) / 2073600]

field_width = (screen_width * 120) / 140
field_height = (screen_height * 85) / 100

players_lock = threading.Lock()
lockazo2 = threading.Lock()
# numeric values that were constants 10 and 8 for a base resolution 1920x1080 rescalated for dynamic res.
grosor = int(screen_width * screen_height/ 207360)
grosor2 = int(screen_width * screen_height/ 259200)

penalty_area_height = (field_height * 55) / 85
penalty_area_width = (field_width * 16.50) / 120

goal_area_height = (field_height * 24.75) / 85
goal_area_width = (field_width * 5.50) / 120

arco_alto = (field_height * 24.75 * 7 / 18) / 85
arco_ancho = (field_width * 24.75 * 2 / 18)/ 85

area_padding = (15 * field_height) / 85
area_padding1 = area_padding + (15.125 * penalty_area_height) / 85
area_padding2 = area_padding1 + (7.5625 * goal_area_height) / 85

pygame.init()
font_size = int(screen_height * screen_width * 36 / 2073600) 
font = pygame.font.Font(None, font_size)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height), flags=pygame.SCALED, vsync=1)


p1_df = pygame.image.load("src/img/p1_df.png")
p1_field = pygame.image.load("src/img/p1_field.png")
p1_st = pygame.image.load("src/img/p1_st.png")
p1_gk = pygame.image.load("src/img/p1_gk.png")

p2_df = pygame.image.load("src/img/p2_df.png")
p2_field = pygame.image.load("src/img/p2_field.png")
p2_st = pygame.image.load("src/img/p2_st.png")
p2_gk = pygame.image.load("src/img/p2_gk.png")

ball_img = pygame.image.load("src/img/ball_3.png")

##### GAME POSITIONS ########

GK = [screen_width - field_width, half_height]

ST = [half_width - 2.5*player_size[0], half_height]

RW = [ST[0] - player_size[0], ST[1] + 3*player_size[0]]
LW = [ST[0] - player_size[0], ST[1] - 3*player_size[0]]

LB = [LW[0] - 5*player_size[0], LW[1] - 2*player_size[0]]
RB = [RW[0] - 5*player_size[0], RW[1] + 2*player_size[0]]
CB_L = [LB[0], LB[1] + 3*player_size[0]]
CB_R = [RB[0], RB[1] - 3*player_size[0]]

CM_L = [CB_L[0] + 5*player_size[0], CB_L[1] - 2*player_size[0]]
CM_M = [CB_L[0] + 4*player_size[0], ST[1]] 
CM_R = [CB_R[0] + 5*player_size[0], CB_R[1] + 2*player_size[0]]


class Ball(pygame.sprite.Sprite): 
    def __init__(self, pos: list[float], coef, field) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.lock = threading.Lock()
        self.field = field
        self.last_pos = pos
        self.pos = pos
        self.coef = coef
        self.vector = (0.0, 0.0)
        self.cont = 0
        self.frozen = False
        self.last_touch = 1
        self.image = ball_img
        self.scaled_ball = pygame.transform.scale(ball_img, ball_size)
        self.img_rect = self.scaled_ball.get_rect(center=(self.pos[0], self.pos[1]))

    def get_vector(self):
        return self.vector

    def reposition(self, pos: list[float]) -> None:
        self.vector = (self.vector[0], 0.0)
        self.pos = pos
        self.img_rect = self.scaled_ball.get_rect(center=(self.pos[0], self.pos[1]))
        
    def draw(self) -> None:
        self.update()
        screen.blit(self.scaled_ball, self.img_rect)
    
    def reset_speed(self) -> None:
        with self.lock:
            self.vector = (self.vector[0], 0.0)

    def stop_ball(self, team_id, player) -> None:
        with self.lock:
            if(self.vector[1] != 0):
                A = player.get_pos()[0]
                B = player.get_pos()[1]
                final = (self.pos[0], self.pos[1])
                recta = (abs(final[0] - A), abs(final[1] - B))
                if(recta[0] < 10 and recta[1] < 10):
                    self.vector = (self.vector[0], 0.0)
                    self.last_touch = team_id

    def get_last_touch(self):
        return self.last_touch

    def get_coef(self):
        return self.coef

    def get_rect(self):
        return self.img_rect

    def get_pos(self) -> list[float]:
        return self.pos

    def get_speed(self) -> list[float]:
        return self.vector[1]

    def get_angle(self) -> float:
        return math.degrees(self.vector[0])

    def get_angle_to_pos(self, target_pos:list[float]) -> float:
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        radians = math.atan2(-dy, dx)
        angle = math.degrees(radians)
        if(angle == -0.0):
            angle = 0.0
        if angle < 0:
            angle += 360
        return (-1*angle + 360)

    def alone(self) -> bool: 
        player0 = field.get_players_team(0)
        player1 = field.get_players_team(1)
        for i in range(1, len(player0)):
            teammate = player0[i]
            enemy = player1[i]
            A = teammate.get_pos()[0]
            B = teammate.get_pos()[1]
            final = (self.pos[0], self.pos[1])
            recta = (abs(final[0] - A), abs(final[1] - B))
            if((recta[0] < 0.8*player_size[0]) and (recta[1] < 0.8*player_size[0])):
                return False
            A = enemy.get_pos()[0]
            B = enemy.get_pos()[1]
            final = (self.pos[0], self.pos[1])
            recta = (abs(final[0] - A), abs(final[1] - B))
            if((recta[0] < 0.8*player_size[0]) and (recta[1] < 0.8*player_size[0])):
                return False
        return True

    def set_angle(self, angle : float):
        self.vector = (math.radians(angle), self.vector[1])

    def hit(self, angle, strength, player) -> None:
        with self.lock:
            if(self.frozen):
                if(self.vector[1] == 0):
                    self.frozen = False
            if(player != None):
                if(self.vector[1] == 0):
                    final = (self.pos[0], self.pos[1])
                    recta = (abs(final[0] - player.get_pos()[0]), abs(final[1] - player.get_pos()[1]))
                    if(recta[0] < 0.8*player_size[0] and recta[1] < 0.8*player_size[0]):
                        self.last_touch = player.get_team().get_side()
                        self.set_angle(angle)
                        self.vector = (self.vector[0], strength)
            else:
                self.set_angle(angle)
                self.vector = (self.vector[0], strength)
                self.frozen = True
            
    def apply_smooth_friction(self, vector):
        angle, z = vector
        z *= (1.059 - self.coef)
        if(int(z) == 0):
            return angle, 0.0
        return angle, z

    def update(self):
        newpos = self.calcnewpos(self.img_rect, self.vector)
        self.img_rect = newpos
        self.vector = self.apply_smooth_friction(self.vector)
        self.pos = self.img_rect.center
        if(self.pos == self.last_pos) and (self.field.get_state() == "Playing") and (not self.alone()):
            if(self.cont < 20):
                self.cont += 1
            else:
                self.cont = 0
                self.hit(random.uniform(0.1, 359.9), 8, None)
        else:
            self.last_pos = self.pos

    def calcnewpos(self, rect, vector):
        (angle, z) = vector
        (dx, dy) = (z * math.cos(angle), z * math.sin(angle))
        return rect.move(dx, dy)

class SoccerField:
    def __init__(self, team_1, team_2, score:list[int]) -> None:
        self.μ = 0.15 
        
        self.set_state("Score")
        self.team_1 = team_1
        self.team_1.set_side(0)
        self.team_2 = team_2
        self.team_2.set_side(1)
        self.last_score = 1
        self.team_1_score = score[0]
        self.team_2_score = score[1]

        self.ball_initial_pos = [half_width, half_height]
        self.ball = Ball(self.ball_initial_pos, self.μ, self)

        self.state_render = font.render(self.state, True, WHITE)

        self.score_line = font.render("-", True, WHITE)
        self.score_team_1 = font.render(f'{self.team_1_score}', True, WHITE)
        self.score_team_2 = font.render(f'{self.team_2_score}', True, WHITE)

        self.center_circle = [half_width,half_height]
        self.middle_line = ([half_width, screen_height-field_height], [half_width, field_height])
        self.bottom_sideline = ([screen_width-field_width,field_height], [field_width,field_height])
        self.upper_sideline = ([screen_width-field_width,screen_height-field_height], [field_width,screen_height-field_height])
        self.left_endline = ([field_width, screen_height-field_height], [field_width, field_height])
        self.right_endline = ([screen_width-field_width, screen_height-field_height], [screen_width-field_width, field_height])
        
        self.top_left_corner = [screen_width-field_width,screen_height-field_height]
        self.top_right_corner = [field_width,screen_height-field_height]
        self.bottom_left_corner = [screen_width-field_width,field_height]
        self.bottom_right_corner = [field_width,field_height]

        self.ls_penalty_area_upper = ([screen_width-field_width, screen_height-field_height+area_padding], [screen_width-field_width+penalty_area_width,screen_height-field_height+area_padding])
        self.ls_penalty_area_bottom = ([screen_width-field_width, field_height-area_padding], [screen_width-field_width+penalty_area_width,field_height-area_padding])
        self.ls_penalty_area_singleline = ([screen_width-field_width+penalty_area_width, screen_height-field_height+area_padding], [screen_width-field_width+penalty_area_width,field_height-area_padding])
        self.ls_goal_area_upper = ([screen_width-field_width,  screen_height-field_height+area_padding1], [screen_width-field_width+goal_area_width,  screen_height-field_height+area_padding1])
        self.ls_goal_area_bottom = ([screen_width-field_width,  screen_height-field_height+area_padding+penalty_area_height-area_padding1], [screen_width-field_width+goal_area_width, screen_height-field_height+area_padding+penalty_area_height-area_padding1])
        self.ls_goal_area_singleline = ([screen_width-field_width+goal_area_width,screen_height-field_height+area_padding1], [screen_width-field_width+goal_area_width,screen_height-field_height+area_padding+penalty_area_height-area_padding1])
        self.ls_arco_area_upper = ([screen_width-field_width,  screen_height-field_height+area_padding2], [screen_width-field_width-arco_ancho,  screen_height-field_height+area_padding2])
        self.ls_arco_area_bottom = ([screen_width-field_width, screen_height-field_height+area_padding+penalty_area_height-area_padding2], [screen_width-field_width-arco_ancho, screen_height-field_height+area_padding+penalty_area_height-area_padding2])
        self.ls_arco_area_singlelane = ([screen_width-field_width-arco_ancho, screen_height-field_height+area_padding2], [screen_width-field_width-arco_ancho, screen_height-field_height+area_padding+penalty_area_height-area_padding2])
        self.ls_penalty_box_arc = [screen_width-field_width+penalty_area_width, half_height]
        self.ls_penalty_kick_mark = [screen_width-field_width+goal_area_width+((penalty_area_width-goal_area_width)/2), half_height]
        
        self.rs_penalty_area_upper = ([field_width, screen_height-field_height+area_padding], [field_width-penalty_area_width,screen_height-field_height+area_padding])
        self.rs_penalty_area_bottom = ([field_width, field_height-area_padding], [field_width-penalty_area_width,field_height-area_padding])
        self.rs_penalty_area_singleline = ([field_width-penalty_area_width, screen_height-field_height+area_padding], [field_width-penalty_area_width,field_height-area_padding])
        self.rs_goal_area_upper = ([field_width,  screen_height-field_height+area_padding1], [field_width-goal_area_width,  screen_height-field_height+area_padding1])
        self.rs_goal_area_bottom = ([field_width,  screen_height-field_height+area_padding+penalty_area_height-area_padding1], [field_width-goal_area_width, screen_height-field_height+area_padding+penalty_area_height-area_padding1])
        self.rs_goal_area_singleline = ([field_width-goal_area_width,screen_height-field_height+area_padding1], [field_width-goal_area_width,screen_height-field_height+area_padding+penalty_area_height-area_padding1])
        self.rs_arco_area_upper = ([field_width,  screen_height-field_height+area_padding2], [field_width+arco_ancho,  screen_height-field_height+area_padding2])
        self.rs_arco_area_bottom = ([field_width, screen_height-field_height+area_padding+penalty_area_height-area_padding2], [field_width+arco_ancho, screen_height-field_height+area_padding+penalty_area_height-area_padding2])
        self.rs_arco_area_singlelane = ([field_width+arco_ancho, screen_height-field_height+area_padding2], [field_width+arco_ancho, screen_height-field_height+area_padding+penalty_area_height-area_padding2])
        self.rs_penalty_box_arc = [field_width-penalty_area_width, half_height]
        self.rs_penalty_kick_mark = [field_width-goal_area_width-((penalty_area_width-goal_area_width)/2), half_height]
        self.background = pygame.Surface((screen_width, screen_height))
        self.draw_on_screen(self.background)

    def change_gametime(self):
        if (self.team_1.get_side() == 0):
            self.team_1.set_side(1)
            self.team_2.set_side(0)
        else:
            self.team_1.set_side(0)
            self.team_2.set_side(1)
        
        aux = self.team_1
        self.team_1 = self.team_2
        self.team_2 = aux

        self.team_1.reposition()
        self.team_2.reposition()
        self.ball.reposition(self.ball_initial_pos)
        
        aux = self.team_1_score
        self.team_1_score = self.team_2_score
        self.team_2_score = aux
        self.last_score = 1
        self.state = "Score"
        self.score_team_1 = font.render(f'{str(self.team_1_score)}', True, WHITE)
        self.score_team_2 = font.render(f'{str(self.team_2_score)}', True, WHITE)

    def set_state(self, state):
        self.state = state
        self.state_render = font.render(self.state, True, WHITE)

    def get_last_score(self):
        return self.last_score

    def get_state(self):
        return self.state

    def get_ball(self) -> Ball:
        return self.ball

    def get_players(self) -> list:
        players = list()
        for player in self.get_players_team(1):
            players.append(player)
        for player in self.get_players_team(2):
            players.append(player)
        return players

    def get_players_team(self, team) -> list:
        if(team == 1):
            return self.team_2.get_players()
        else:
            return self.team_1.get_players()

    def get_team(self, team) -> None:
        if 0 == self.team_1.get_side():
            return self.team_1
        elif 1 == self.team_2.get_side():
            return self.team_2

    def draw(self):
        screen.blit(self.background, (0, 0))
        
        screen.blit(self.state_render, (int(self.middle_line[0][0] / 2), int(self.top_left_corner[1]/2)))
        screen.blit(self.score_team_1, (int(self.middle_line[0][0]- (font_size*2) - (grosor/2)), int(self.top_left_corner[1]/2)))
        screen.blit(self.score_team_2, (int(self.middle_line[0][0]+ (font_size*2) - (grosor/2)), int(self.top_left_corner[1]/2)))

    def draw_on_screen(self, screen) -> None:
        screen.fill(GREEN)
        # center circle
        pygame.draw.circle(screen, WHITE, self.center_circle, penalty_area_width/2, grosor)

        # middlefield band
        pygame.draw.line(screen, WHITE, self.middle_line[0], self.middle_line[1], grosor)

        # field sidelines
        pygame.draw.line(screen, WHITE, self.upper_sideline[0], self.upper_sideline[1], grosor)
        pygame.draw.line(screen, WHITE, self.bottom_sideline[0], self.bottom_sideline[1], grosor)

        # field endlines
        pygame.draw.line(screen, WHITE, self.left_endline[0], self.left_endline[1], grosor)
        pygame.draw.line(screen, WHITE, self.right_endline[0], self.right_endline[1], grosor)

    
        # LEFT SIDE

        # penalty area

        pygame.draw.line(screen, (203,203,203), self.ls_penalty_area_upper[0], self.ls_penalty_area_upper[1], grosor)
        pygame.draw.line(screen, (203,203,203), self.ls_penalty_area_bottom[0], self.ls_penalty_area_bottom[1], grosor)

        pygame.draw.line(screen, (203,203,203), self.ls_penalty_area_singleline[0], self.ls_penalty_area_singleline[1], grosor)


        # goal area
        pygame.draw.line(screen, (166,166,166), self.ls_goal_area_upper[0], self.ls_goal_area_upper[1], grosor)
        pygame.draw.line(screen, (166,166,166), self.ls_goal_area_bottom[0], self.ls_goal_area_bottom[1], grosor)

        pygame.draw.line(screen,  (166,166,166), self.ls_goal_area_singleline[0], self.ls_goal_area_singleline[1], grosor)


        # arco 

        # rects for collision
        self.ls_palo_upper = pygame.Rect(self.ls_arco_area_upper[1][0], self.ls_arco_area_upper[0][1], abs(self.ls_arco_area_upper[1][0] - self.ls_arco_area_upper[0][0]), grosor2)
        self.ls_palo_bottom = pygame.Rect(self.ls_arco_area_bottom[1][0], self.ls_arco_area_bottom[0][1], abs(self.ls_arco_area_bottom[1][0] - self.ls_arco_area_bottom[0][0]), grosor2)
        
        pygame.draw.rect(screen, (129,129,129), self.ls_palo_upper, grosor2)
        pygame.draw.rect(screen, (129,129,129), self.ls_palo_bottom, grosor2)

        pygame.draw.line(screen, (129,129,129), self.ls_arco_area_singlelane[0], self.ls_arco_area_singlelane[1], grosor)

        # penalty box arc
        pygame.draw.circle(screen, (221,221,221), self.ls_penalty_box_arc, penalty_area_width/2, grosor, True, False, False, True)

        # penalty kick mark
        pygame.draw.circle(screen, (0,0,0), self.ls_penalty_kick_mark, grosor, grosor)

        # corner marks
        pygame.draw.circle(screen, WHITE, self.top_left_corner, int(goal_area_width/2), grosor, False, False, False, True)
        pygame.draw.circle(screen, WHITE, self.top_right_corner, int(goal_area_width/2), grosor, False, False, True, False)
        pygame.draw.circle(screen, WHITE, self.bottom_left_corner, int(goal_area_width/2), grosor, True, False, False, False)
        pygame.draw.circle(screen, WHITE, self.bottom_right_corner, int(goal_area_width/2), grosor, False, True, False, False)


        # RIGHT SIDE

        # penalty area

        pygame.draw.line(screen, (203,203,203), self.rs_penalty_area_upper[0], self.rs_penalty_area_upper[1], grosor)
        pygame.draw.line(screen, (203,203,203), self.rs_penalty_area_bottom[0], self.rs_penalty_area_bottom[1], grosor)

        pygame.draw.line(screen, (203,203,203), self.rs_penalty_area_singleline[0], self.rs_penalty_area_singleline[1], grosor)

        # goal area
        pygame.draw.line(screen, (166,166,166), self.rs_goal_area_upper[0], self.rs_goal_area_upper[1], grosor)
        pygame.draw.line(screen, (166,166,166), self.rs_goal_area_bottom[0], self.rs_goal_area_bottom[1], grosor)

        pygame.draw.line(screen,  (166,166,166), self.rs_goal_area_singleline[0], self.rs_goal_area_singleline[1], grosor)

        # arco 

        # rects for collision
        self.rs_palo_upper = pygame.Rect(self.rs_arco_area_upper[0][0], self.rs_arco_area_upper[0][1], abs(self.rs_arco_area_upper[1][0] - self.rs_arco_area_upper[0][0]), grosor2)
        self.rs_palo_bottom = pygame.Rect(self.rs_arco_area_bottom[0][0], self.rs_arco_area_bottom[0][1], abs(self.rs_arco_area_bottom[1][0] - self.rs_arco_area_bottom[0][0]), grosor2)
        
        pygame.draw.rect(screen, (129,129,129), self.rs_palo_upper, grosor2)
        pygame.draw.rect(screen, (129,129,129), self.rs_palo_bottom, grosor2)

        pygame.draw.line(screen, (129,129,129), self.rs_arco_area_singlelane[0], self.rs_arco_area_singlelane[1], grosor)

        # penalty kick mark
        pygame.draw.circle(screen, (0,0,0), self.rs_penalty_kick_mark, grosor, grosor)

        # penalty box arc
        pygame.draw.circle(screen, (221,221,221), self.rs_penalty_box_arc, penalty_area_width/2, grosor, False, True, True, False)
        
        
        screen.blit(self.score_line, (int(self.middle_line[0][0] - (grosor/2)), int(self.top_left_corner[1]/2)))
     
    def goal(self) -> int:
        if (self.ball.get_rect().midright[0] < self.ls_arco_area_bottom[0][0]) and (self.ball.get_rect().midright[1] > self.ls_arco_area_singlelane[0][1] and self.ball.get_rect().midright[1] < self.ls_arco_area_singlelane[1][1]):
            self.team_2_score += 1
            self.last_score = 1
            self.score_team_2 = font.render(f'{str(self.team_2_score)}', True, WHITE)
            self.ball.reset_speed()
            self.ball.reposition(self.ball_initial_pos)
            self.team_1.reposition()
            self.team_2.reposition()
            self.set_state("Score")
            time.sleep(0.5)
            
            
        elif self.ball.get_rect().midleft[0] > self.rs_arco_area_bottom[0][0] and (self.ball.get_rect().midleft[1] > self.rs_arco_area_singlelane[0][1] and self.ball.get_rect().midright[1] < self.rs_arco_area_singlelane[1][1]):
            self.team_1_score += 1
            self.last_score = 0
            self.score_team_1 = font.render(f'{str(self.team_1_score)}', True, WHITE)
            self.ball.reset_speed()
            self.ball.reposition(self.ball_initial_pos)
            self.get_ball().get_angle_to_pos([self.rs_arco_area_bottom[0][0], self.rs_penalty_kick_mark[1]]) 
            self.team_1.reposition()
            self.team_2.reposition()
            self.set_state("Score")
            time.sleep(0.5)

    def throw_in(self) -> None:
        if self.ball.get_pos()[1] <= screen_height - field_height: 
            self.set_state("Out of Game")
            self.ball.reset_speed()
            self.ball.reposition([self.ball.pos[0], self.upper_sideline[0][1] + 0.5*ball_size[0]])

        elif self.ball.get_pos()[1] >= field_height:
            self.set_state("Out of Game")
            self.ball.reset_speed()
            self.ball.reposition([self.ball.pos[0], self.bottom_sideline[0][1] - 0.5*ball_size[0]])

    def corner(self) -> None:
        if self.ball.get_rect().midright[0] < field.top_left_corner[0]:
            if self.ball.get_rect().midbottom[1] <= self.ls_arco_area_singlelane[0][1]:
                # corner arriba izquierda
                self.ball.reset_speed()
                if (self.ball.last_touch == self.team_2.get_side()):
                    self.set_state("Goal Kick")
                    self.ball.reposition([screen_width - field_width, half_height])
                else:
                    self.set_state("Out of Game")
                    self.ball.reposition(self.top_left_corner)


            elif self.ball.get_rect().midbottom[1] >= self.ls_arco_area_singlelane[1][1]:
                # corner abajo izquierda
                self.ball.reset_speed()
                if (self.ball.last_touch == self.team_2.get_side()):
                    self.set_state("Goal Kick")
                    self.ball.reposition([screen_width - field_width, half_height])
                else:
                    self.set_state("Out of Game")
                    self.ball.reposition(self.bottom_left_corner)
 

        elif self.ball.get_rect().midleft[0] > self.top_right_corner[0]:
            if self.ball.get_rect().midtop[1] <= self.rs_arco_area_singlelane[0][1]:
                # corner arriba derecha
                self.ball.reset_speed()
                if (self.ball.last_touch == self.team_1.get_side()):
                    self.set_state("Goal Kick")
                    self.ball.reposition([field_width, half_height])
                else:
                    self.set_state("Out of Game")
                    self.ball.reposition(self.top_right_corner)


            elif self.ball.get_rect().midtop[1] >= self.rs_arco_area_singlelane[1][1]:
                # corner abajo derecha
                self.ball.reset_speed()
                if (self.ball.last_touch == self.team_1.get_side()):
                    self.set_state("Goal Kick")
                    self.ball.reposition([field_width, half_height])
                else:
                    self.set_state("Out of Game")
                    self.ball.reposition(self.bottom_right_corner)

    def palo(self) -> None: # PELIGROSO
        # arco derecho lado izquierdo ambos palos
        if any(self.ball.get_rect().collidepoint(self.rs_palo_bottom.left, y) for y in range(self.rs_palo_bottom.top, self.rs_palo_bottom.bottom + 1)) or any(self.ball.get_rect().collidepoint(self.rs_palo_upper.left, y) for y in range(self.rs_palo_upper.top, self.rs_palo_upper.bottom + 1)):
            if(self.ball.get_angle() > 270):
                self.ball.hit(-1*(self.ball.get_angle()) + 540, self.ball.get_speed() + 1, None)
            else:
                self.ball.hit(-1*(self.ball.get_angle() - 180), self.ball.get_speed() + 1, None)

        # arco izquierdo lado derecho ambos palos
        elif any(self.ball.get_rect().collidepoint(self.ls_palo_bottom.right, y) for y in range(self.ls_palo_bottom.top, self.ls_palo_bottom.bottom + 1)) or any(self.ball.get_rect().collidepoint(self.ls_palo_upper.right, y) for y in range(self.ls_palo_upper.top, self.ls_palo_upper.bottom + 1)):
            if(self.ball.get_angle() <= 180):
                self.ball.hit(-1*(self.ball.get_angle() - 180), self.ball.get_speed() + 1, None)
            else:
                self.ball.hit(-1*(self.ball.get_angle()) + 540, self.ball.get_speed() + 1, None)

        # ambos arcos ambos palos arriba abajo
        elif any(self.ball.get_rect().collidepoint(x, self.ls_palo_bottom.top) for x in range(self.ls_palo_bottom.left, self.ls_palo_bottom.right + 1)) or any(self.ball.get_rect().collidepoint(x, self.ls_palo_upper.top) for x in range(self.ls_palo_upper.left, self.ls_palo_upper.right + 1)) or any(self.ball.get_rect().collidepoint(x, self.ls_palo_bottom.bottom) for x in range(self.ls_palo_bottom.left, self.ls_palo_bottom.right + 1)) or any(self.ball.get_rect().collidepoint(x, self.ls_palo_upper.bottom) for x in range(self.ls_palo_upper.left, self.ls_palo_upper.right + 1)) or any(self.ball.get_rect().collidepoint(x, self.rs_palo_bottom.top) for x in range(self.rs_palo_bottom.left, self.rs_palo_bottom.right + 1)) or any(self.ball.get_rect().collidepoint(x, self.rs_palo_upper.top) for x in range(self.rs_palo_upper.left, self.rs_palo_upper.right + 1)) or any(self.ball.get_rect().collidepoint(x, self.rs_palo_bottom.bottom) for x in range(self.rs_palo_bottom.left, self.rs_palo_bottom.right + 1)) or any(self.ball.get_rect().collidepoint(x, self.rs_palo_upper.bottom) for x in range(self.rs_palo_upper.left, self.rs_palo_upper.right + 1)) :
            self.ball.hit(-1*self.ball.get_angle() + 360, self.ball.get_speed() + 1, None)

    def begin(self) -> None: 
        self.team_1.start()
        self.team_2.start()
        
class Fov:
    def __init__(self, angle, pos:list[float]) -> None:
        self.angle = angle
        self.pos = pos
    
    def draw(self):
        # punto inicial x
        A = self.pos[0]

        # punto inicial y
        B = self.pos[1]

        inicio = (A,B)
        # grado de vision osea miro al grado
        z = self.angle
        zrad = math.radians(z)
        RestaSumaRad = math.radians(50)

        #distancia cono
        L = (screen_width * screen_height * 45) / 2073600
        extremo_x = A + L * math.cos(zrad)
        extremo_y = B + L * math.sin(zrad)

        # recta de esos grados desde el punto inicial
        self.extremo = [extremo_x, extremo_y]

        #recta de grados menos
        if(z < 50):
            calculo = z - 50 + 360
            calculoRad = math.radians(calculo)
            extremo_resta_x = A + L * math.cos(calculoRad)
            extremo_resta_y = B + L * math.sin(calculoRad)
        else:
            extremo_resta_x = A + L * math.cos(zrad - RestaSumaRad)
            extremo_resta_y = B + L * math.sin(zrad - RestaSumaRad)
        self.extremo_resta = [extremo_resta_x, extremo_resta_y]

        #recta de grados mas
        if(z >= 310):
            calculo = z - 360 + 50
            calculoRad = math.radians(calculo)
            extremo_suma_x = A + L * math.cos(calculoRad)
            extremo_suma_y = B + L * math.sin(calculoRad)
        else:
            extremo_suma_x = A + L * math.cos(zrad + RestaSumaRad)
            extremo_suma_y = B + L * math.sin(zrad + RestaSumaRad)
            
        self.extremo_suma = [extremo_suma_x, extremo_suma_y]

        grosor_fov = int(grosor*0.7)
        pygame.draw.line(screen, (209, 209, 209), inicio, self.extremo, grosor_fov)

        pygame.draw.line(screen, (209, 209, 209), inicio, self.extremo_resta, grosor_fov)
        pygame.draw.line(screen, (209, 209, 209), inicio, self.extremo_suma, grosor_fov)

        pygame.draw.line(screen, (209, 209, 209), self.extremo_resta, self.extremo, grosor_fov)
        pygame.draw.line(screen, (209, 209, 209), self.extremo, self.extremo_suma, grosor_fov)

    def set_pos(self, pos:list[float]):
        self.pos = pos

    def set_angle(self, angle):
        self.angle = angle

    def is_sprite_at_view(self, sprite):
        third_part_field = field_width/3
        half_field_height = field_height/2

        fov_rect = pygame.Rect(0, 0, third_part_field, half_field_height)
        original_surface = pygame.Surface((third_part_field, half_field_height), pygame.SRCALPHA)
        bottom_right_rect = original_surface.get_rect(center=fov_rect.center)
        bottom_right_rect.topleft = [self.pos[0], self.pos[1]]

        if 50 >= self.angle >= 40:
            return bottom_right_rect.colliderect(sprite.get_rect())
        
        elif 140 >= self.angle >= 130:
            bottom_left_rect = bottom_right_rect.move(-bottom_right_rect.width, 0)
            return bottom_left_rect.colliderect(sprite.get_rect())
        
        elif 230 >= self.angle >= 220:
            upper_left_rect = bottom_right_rect.move(-bottom_right_rect.width, -bottom_right_rect.height)
            return upper_left_rect.colliderect(sprite.get_rect())
         
        elif 320 >= self.angle >= 310:
            upper_right_rect = bottom_right_rect.move(0, -bottom_right_rect.height)
            return upper_right_rect.colliderect(sprite.get_rect())

        elif 45 < self.angle < 135:
            bottom_left_rect = bottom_right_rect.move(-bottom_right_rect.width, 0)
            return bottom_right_rect.colliderect(sprite.get_rect()) or bottom_left_rect.colliderect(sprite.get_rect())
            
        elif 225 > self.angle > 135:
            bottom_left_rect = bottom_right_rect.move(-bottom_right_rect.width, 0)
            upper_left_rect = bottom_right_rect.move(-bottom_right_rect.width, -bottom_right_rect.height)
            return bottom_left_rect.colliderect(sprite.get_rect()) or upper_left_rect.colliderect(sprite.get_rect())

        elif 315 > self.angle > 225:
            upper_left_rect = bottom_right_rect.move(-bottom_right_rect.width, -bottom_right_rect.height)
            upper_right_rect = bottom_right_rect.move(0, -bottom_right_rect.height)
            return upper_left_rect.colliderect(sprite.get_rect()) or upper_right_rect.colliderect(sprite.get_rect())
            
        elif 45 > self.angle or self.angle > 315:
            upper_right_rect = bottom_right_rect.move(0, -bottom_right_rect.height)
            return bottom_right_rect.colliderect(sprite.get_rect()) or upper_right_rect.colliderect(sprite.get_rect())
        else:
            return False

    def get_angle_to_object(self, target) -> float:
        if(target.pos[1] == self.pos[1]) and (target.pos[0] == self.pos[0]):
            return 0
        else:
            dx = target.pos[0] - self.pos[0]
            dy = target.pos[1] - self.pos[1]
            radianes = math.atan2(-dy, dx)
            angulo = math.degrees(radianes)
            if angulo < 0:
                angulo += 360
            return -1*angulo + 360
        
    def get_angle_to_pos(self, target_pos:list[float]) -> float:
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        radianes = math.atan2(-dy, dx)
        angulo = math.degrees(radianes)
        if angulo < 0:
            angulo += 360
        return -1*angulo + 360

class Player(threading.Thread, pygame.sprite.Sprite):
    def __init__(self, name, speed, strength, img_path):
        pygame.sprite.Sprite.__init__(self)
        threading.Thread.__init__(self)
        self.name = name
        self.pos = [0.0,0.0]
        self.speed = speed
        self.side = -1
        self.strength = strength
        self.image = img_path
        self.fov = Fov(0.0, self.pos)
        self.vector = (0.0, 0.0)
        self.scaled_player = pygame.transform.scale(self.image, player_size) # to-do: rescalar dinamicamente
        self.img_rect = self.scaled_player.get_rect(center=(self.pos))

    def get_side(self):
        return self.side

    def set_side(self, old_side, new_side): # side 0 lado izq 1 lado derecho
        if new_side == 0:
            self.set_angle(0)
            self.fov.set_angle(0)
            self.behaviour.set_arco_line([[field_width,  screen_height-field_height+area_padding2], [field_width, screen_height-field_height+area_padding+penalty_area_height-area_padding2]])
        
        elif new_side == 1:
            self.set_angle(180)
            self.fov.set_angle(180)
            self.behaviour.set_arco_line([[screen_width-field_width,  screen_height-field_height+area_padding2], [screen_width-field_width, screen_height-field_height+area_padding+penalty_area_height-area_padding2]])
        
        if old_side != new_side:
            self.set_pos([screen_width - self.behaviour.get_pos()[0], screen_height - self.behaviour.get_pos()[1]])
            self.behaviour.set_pos(self.get_pos())
            self.img_rect = self.scaled_player.get_rect(center=(self.pos[0], self.pos[1]))
            self.side = new_side
    
    def get_name(self):
        return self.name

    def get_fov(self) -> Fov:
        return self.fov
        
    def set_behaviour(self, behaviour):
        self.behaviour = behaviour
        self.initial_pos = behaviour.get_pos()
        self.set_pos(self.initial_pos)
        self.img_rect = self.scaled_player.get_rect(center=(self.pos[0], self.pos[1]))

    def get_rect(self):
        return self.img_rect

    def get_pos(self) -> list[float]:
        return self.pos

    def set_pos(self, pos:list[float]):
        self.pos = pos
        self.fov.set_pos(self.pos)

    def set_team(self, team):
        self.team = team
        self.side = self.team.get_side()

    def get_vector(self):
        return self.vector

    def get_team(self):
        return self.team

    def get_angle(self) -> float:
        return math.degrees(self.vector[0])

    def set_angle(self, angle : float):
        self.vector = (math.radians(angle), self.vector[1])
        self.fov.set_angle(self.get_angle())

    def reposition(self):
        self.pos = self.behaviour.get_pos()
        self.img_rect = self.scaled_player.get_rect(center=(self.pos[0], self.pos[1]))
        self.fov.set_pos(self.pos)
        if self.team.get_side() == 0:
            self.vector = (0.0, 0.0)
            self.fov.set_angle(0)
        else:
            self.vector = (180.0, 0.0)
            self.fov.set_angle(180)

    def draw(self) -> None:
        self.update()
        self.fov.draw()
        screen.blit(self.scaled_player, self.img_rect)

    def set_speed(self, speed):
        self.vector = (self.vector[0], speed)

    def get_speed(self) -> float:
        return self.speed

    def get_strength(self) -> float:
        return self.strength

    def run(self) -> None:
        while True:
            self.behaviour.flow()
            time.sleep(1/30)

    def move_arquero(self, angle, speed):
        self.set_vector(vector=(angle, speed))

    def move(self, angle, speed):
        if((self.pos[0] > screen_width - field_width and self.pos[0] < field_width) and 
        (self.pos[1] > screen_height - field_height and self.pos[1] < field_height)):
            self.set_vector(vector=(angle, speed))
        else:
            new_angle = self.fov.get_angle_to_pos(self.behaviour.pos)
            self.set_vector(vector=(new_angle, self.speed))
            time.sleep(1)

    def set_vector(self, vector):
        self.fov.set_angle(vector[0])
        if(vector[1] <= self.speed):
            self.vector = (math.radians(vector[0]), vector[1])
        else:
            self.vector = (math.radians(vector[0]), self.speed)

    def update(self):
        newpos = self.calcnewpos(self.img_rect, self.vector)
        self.img_rect = newpos
        self.fov.set_pos([self.img_rect.centerx, self.img_rect.centery])
        self.pos = [self.img_rect.centerx, self.img_rect.centery]

    def calcnewpos(self, rect, vector):
        (angle, z) = vector
        (dx, dy) = (z * math.cos(angle), z * math.sin(angle))
        return rect.move(dx, dy)

    def kick_with_angle(self, angle, strength):
        if(strength <= self.strength):
            self.team.get_field().get_ball().hit(angle, strength, self)
        else:
            self.team.get_field().get_ball().hit(angle, self.strength, self)

    def kick(self, target_pos, strength):
        angle = self.team.get_field().get_ball().get_angle_to_pos(target_pos)
        self.kick_with_angle(angle, strength)

    def stop_ball(self):
        self.team.get_field().get_ball().stop_ball(self.team.get_name(), self)

class Behaviour():
    def __init__(self, pos:list[float])-> None:
        self.pos = pos

    def get_pos(self) -> list[float]:
        return self.pos

    def get_arco_line(self):
        return self.arco_line

    def set_arco_line(self, rect):
        self.arco_line = rect

    def set_pos(self, pos):
        self.pos = pos

    def set_player(self, player):
        self.player = player

    def flow(self):
        return None

    def stop_ball(self):
        self.player.stop_ball()

    def spin(self, angle) -> bool:
        z = 6 # 360grados en 1s
        my_angle = self.player.get_angle()
        y = angle
        x = my_angle
        diferencia = (y - x) % 360  # Calcula la diferencia entre y y x
        if diferencia <= z or diferencia >= 360 - z:
            self.player.set_angle(y)
            return True
        else:
            diferencia_corta = min(diferencia, 360 - diferencia)  # Calcula la distancia más corta
            if diferencia == diferencia_corta:
                self.player.set_angle(y)
                return True 
            else:
                if y > x:
                    nuevo_y = (x + z) % 360  # Calcula el nuevo ángulo sumando el límite al ángulo inicial
                else:
                    nuevo_y = (x - z) % 360  # Calcula el nuevo ángulo restando el límite al ángulo inicial
                self.player.set_angle(nuevo_y)
                return False  

    def player_has_ball(self) -> Player | None:
        ball = self.player.get_team().get_field().get_ball()
        side = self.player.get_side()
        if side == 0:
            enemy_side = 1
        else:
            enemy_side = 0

        nearest_teammate =  None
        nearest_teammate_distance = screen_width

        nearest_enemy = None
        nearest_enemy_distance = screen_width

        teammates = self.player.get_team().get_field().get_players_team(side)
        enemies = self.player.get_team().get_field().get_players_team(enemy_side)

        target = ball.get_pos()

        for i in range(1, len(teammates)):
            teammate = teammates[i]
            enemy = enemies[i]


            distance_teammate = math.sqrt(((target[0] - teammate.get_pos()[0])**2 + (target[1]  - teammate.get_pos()[1])**2))
            distance_enemy = math.sqrt(((target[0] - enemy.get_pos()[0])**2 + (target[1]  - enemy.get_pos()[1])**2))

            if (distance_teammate < nearest_teammate_distance):
                nearest_teammate_distance = distance_teammate
                nearest_teammate = teammate

            if (distance_enemy < nearest_enemy_distance):
                nearest_enemy_distance = distance_enemy
                nearest_enemy = enemy

        the_nearest = None

        if (distance_teammate < distance_enemy) and ( nearest_teammate_distance < 0.8*player_size[0]):
            the_nearest = nearest_teammate
        elif (nearest_enemy_distance < 0.8*player_size[0]):
            the_nearest = nearest_enemy
        return [the_nearest, nearest_teammate]
    
    def free_path(self, pos:list[float]) -> bool:

        if(pos[1] >= field_height or pos[1] <= screen_height - field_height):
            return False

        side = self.player.get_side()
        if side == 0:
            if(pos[0] >= field_width):
                return False
            enemy_side = 1
        else:
            if(pos[0] <= screen_width - field_width):
                return False
            enemy_side = 0
        
        my_angle = self.player.get_fov().get_angle_to_pos(pos)
        while not self.spin(my_angle):
            pass
        
        teammates = self.player.get_team().get_field().get_players_team(side)
        enemies = self.player.get_team().get_field().get_players_team(enemy_side)

        for i in range(1, len(teammates)):
            teammate = teammates[i]
            enemy = enemies[i]
            if(self.player.get_fov().is_sprite_at_view(teammate) and self.player is not teammate):
                player_angle = self.player.get_fov().get_angle_to_pos(teammate.get_pos())
                if(abs(my_angle - player_angle) < 6):
                    return False
            
            if(self.player.get_fov().is_sprite_at_view(enemy)):
                player_angle = self.player.get_fov().get_angle_to_pos(enemy.get_pos())
                if(abs(my_angle - player_angle) < 6):
                    return False

        return True
    
    def free_teammate(self, forward_pass:bool) -> Player:
        teammates_at_view = list()
        for teammate in self.player.get_team().get_players():
            if(self.player.get_fov().is_sprite_at_view(teammate)):
                teammates_at_view.append(teammate)
        side = self.player.get_side()
        if  side == 0:
            enemy_team = 1
        else:
            enemy_team = 0

        enemies_at_view = list()
        for enemy in self.player.get_team().get_field().get_players_team(enemy_team):
            if(self.player.get_fov().is_sprite_at_view(enemy)):
                enemies_at_view.append(enemy)

        if(forward_pass):
            for free in teammates_at_view:
                if free is not self.player:
                    flag = True
                    distance = math.sqrt(((self.get_pos()[0] - free.get_pos()[0])**2 + (self.get_pos()[1] - free.get_pos()[1])**2))
                    for enemy in enemies_at_view:
                        if(abs(self.player.get_fov().get_angle_to_pos(free.get_pos()) - self.player.get_fov().get_angle_to_pos(enemy.get_pos())) < 6):
                            enemy_distance = math.sqrt(((self.get_pos()[0] - enemy.get_pos()[0])**2 + (self.get_pos()[1] - enemy.get_pos()[1])**2))
                            if(distance >= enemy_distance):
                                flag = False
                                break
                    if(side == 0):
                        if(self.player.get_pos()[0] < free.get_pos()[0]):
                            return free
                    else:
                        if(self.player.get_pos()[0] > free.get_pos()[0]):
                            return free
            return None
        else:
            nearest =  None
            nearest_distance = 1920

            for free in teammates_at_view:
                if free is not self.player:
                    flag = True
                    distance = math.sqrt(((self.get_pos()[0] - free.get_pos()[0])**2 + (self.get_pos()[1] - free.get_pos()[1])**2))
                    for enemy in enemies_at_view:
                        if(abs(self.player.get_fov().get_angle_to_pos(free.get_pos()) - self.player.get_fov().get_angle_to_pos(enemy.get_pos())) < 6):
                            enemy_distance = math.sqrt(((self.get_pos()[0] - enemy.get_pos()[0])**2 + (self.get_pos()[1] - enemy.get_pos()[1])**2))
                            if(distance >= enemy_distance):
                                flag = False
                                break
                    
                    if((nearest == None or distance < nearest_distance) and flag):
                        nearest = free
                        nearest_distance = distance

            return nearest
    
    def aim_and_kick(self):
        side = self.player.get_side()
        if side == 0:
            enemy_team = 1
        else:
            enemy_team = 0
        goalkeeper = self.player.get_team().get_field().get_team(enemy_team).get_player(0)
        angle =  self.player.get_fov().get_angle_to_object(goalkeeper)

        upper_angle = self.player.get_fov().get_angle_to_pos(self.get_arco_line()[0])
        bottom_angle = self.player.get_fov().get_angle_to_pos(self.get_arco_line()[1])

        distance_to_upper = abs(angle - upper_angle)
        distance_to_bottom = abs(angle - bottom_angle)

        self.player.set_speed(0.0)
        self.player.stop_ball()
        if (side == 0):
            if (distance_to_upper < distance_to_bottom):
                self.player.kick_with_angle(upper_angle + 4, self.player.get_strength())
            else:
                self.player.kick_with_angle(bottom_angle - 4, self.player.get_strength())
        else:
            if (distance_to_upper < distance_to_bottom):
                self.player.kick_with_angle(upper_angle - 4, self.player.get_strength())
            else:
                self.player.kick_with_angle(bottom_angle + 4, self.player.get_strength())

    def aim_and_pass(self, target):
        angle = self.player.get_fov().get_angle_to_object(target)
        self.player.set_speed(0.0)
        self.player.stop_ball()
        distance = math.sqrt(((self.player.get_pos()[0] - target.get_pos()[0])**2 + (self.player.get_pos()[1] - target.get_pos()[0])**2))
        coef_strenght = ((distance * (player_size[0]/2)) / (5*player_size[0]))
        #5jugadores * 25f / 245
        self.player.kick_with_angle(angle, coef_strenght*self.player.get_strength())

    def team_posession(self) -> bool:
        return self.player.get_team().get_field().get_ball().get_last_touch() == self.player.get_side()

    def hold_ball(self):
        move_right = [self.player.get_pos()[0] + 2*player_size[0], self.player.get_pos()[1] + random.choice([2*player_size[0], -2*player_size[0]])]
        move_left = [self.player.get_pos()[0] - 2*player_size[0], self.player.get_pos()[1] + random.choice([2*player_size[0], -2*player_size[0]])]
        if(self.player.get_side() == 0):
            if(self.free_path(move_right)):
                self.move_with_ball(self.player.get_fov().get_angle_to_pos(move_right))
            else:
                self.move_with_ball(self.player.get_fov().get_angle_to_pos(move_left))
        else:
            if(self.free_path(move_left)):
                self.move_with_ball(self.player.get_fov().get_angle_to_pos(move_left))
            else:
                self.move_with_ball(self.player.get_fov().get_angle_to_pos(move_right))

    def intercept(self, speed):
        ball = self.player.get_team().get_field().get_ball()
        ball_pos = ball.get_pos()
        ball_angle = ball.get_angle()
        ball_speed = ball.get_speed()
        player_speed = speed

        ball_speed *= (1.059 - ball.get_coef())

        if (int(ball_speed) == 0):
            ball_speed = 0

        new_ball_x = ball_pos[0] + ball_speed * math.cos(math.radians(ball_angle))
        new_ball_y = ball_pos[1] + ball_speed * math.sin(math.radians(ball_angle))

        old_distance = math.sqrt(((self.player.get_pos()[0] - ball_pos[0])**2 + (self.get_pos()[1] - ball_pos[1])**2))
        new_distance = math.sqrt(((self.player.get_pos()[0] - new_ball_x)**2 + (self.get_pos()[1] - new_ball_y)**2))
        if (old_distance > new_distance and new_distance < 4 * player_size[0]):
            self.player.move(self.player.fov.get_angle_to_pos([new_ball_x, new_ball_y]), player_speed)
        if(self.player_has_ball()):
            self.player.set_speed(0.0)
            self.player.stop_ball()
    
    def action_blind(self):
        return None
    
    def goal_kick(self):
        return None

    def out_of_game(self):
        return None
    
    def pos_in_goal_area_rs(self, pos:list[float]) -> bool:
        return (pos[0] >= self.player.get_team().get_field().rs_penalty_box_arc[0] and 
            ((pos[1] >= self.player.get_team().get_field().rs_goal_area_upper[0][1]) and 
            (pos[1] <= self.player.get_team().get_field().rs_goal_area_bottom[0][1])) ) 
            
    def pos_in_goal_area_ls(self, pos:list[float]) -> bool: 
        return (pos[0] <= self.player.get_team().get_field().ls_penalty_box_arc[0] and 
            ((pos[1] >= self.player.get_team().get_field().ls_goal_area_upper[0][1]) and 
            (pos[1] <= self.player.get_team().get_field().ls_goal_area_bottom[0][1])))

class GoalkeeperBehaviour(Behaviour):
    def __init__(self, pos: list[float]) -> None:
        super().__init__(pos)
        self.cont = 0

    def player_has_ball(self) -> bool:
        A = self.player.get_pos()[0]
        B = self.player.get_pos()[1]
        final = (self.player.get_team().get_field().get_ball().get_pos()[0], self.player.get_team().get_field().get_ball().get_pos()[1])
        recta = (abs(final[0] - A), abs(final[1] - B))
        if(recta[0] < player_size[0]*0.1 and recta[1] < player_size[0]*0.1):
            return True
        return False

    def free_teammate(self, forward_pass: bool) -> Player:
        teammates_at_view = list()
        for teammate in self.player.get_team().get_players():
            if(self.player.get_fov().is_sprite_at_view(teammate)):
                teammates_at_view.append(teammate)
        for free in teammates_at_view:
            if free is not self.player:
                return free

    def flow(self):
        game_state = self.player.get_team().get_field().get_state()
        if(game_state != "Goal Kick"):
            if(not (self.get_arco_line()[1][1] > self.player.get_pos()[1] > self.get_arco_line()[0][1])):
                self.action_blind()
            if((self.player.get_fov().is_sprite_at_view(self.player.get_team().get_field().get_ball())) and 
                not self.player_has_ball()):
                if(self.player.get_side() == 0):
                    if(self.pos_in_goal_area_ls(self.player.get_team().get_field().get_ball().get_pos())):
                        self.follow_ball()
                if(self.player.get_side() == 1):
                    if(self.pos_in_goal_area_rs(self.player.get_team().get_field().get_ball().get_pos())):
                        self.follow_ball()
            elif self.player_has_ball():
                self.player.set_speed(0.0)
                self.player.stop_ball()
                target = self.free_teammate(True)
                if target is not None:
                    self.aim_and_pass(target)
                    self.cont = 0
                else:
                    self.cont +=1
                    if(self.cont > 30):
                        if(self.player.get_side() == 1):
                            self.player.kick_with_angle(random.choice([135, 225]), self.player.get_strength())
                            time.sleep(0.2)
                            self.cont = 0
                        else:
                            self.player.kick_with_angle(random.choice([45, 315]), self.player.get_strength())
                            time.sleep(0.2)
                            self.cont = 0
            else:
                self.action_blind()
        else:
            self.goal_kick()
                      
    def action_blind(self):
        if(self.player.get_pos()[1] != half_height):
            self.player.move_arquero(self.player.get_fov().get_angle_to_pos([self.pos[0], half_height]), self.player.get_speed()*0.5)
        else:
            self.player.set_speed(0.0)
            self.player.set_angle(self.player.get_fov().get_angle_to_object(self.player.get_team().get_field().get_ball()))

    def follow_ball(self):
        ball = self.player.get_team().get_field().get_ball()
        if(self.get_arco_line()[1][1] > self.player.get_pos()[1] > self.get_arco_line()[0][1]):
            if(self.get_arco_line()[1][1] > ball.get_pos()[1] > self.get_arco_line()[0][1]):
                if(self.player.get_pos()[1] < ball.get_pos()[1]):
                    self.player.move_arquero(90, ball.get_speed())
                elif(self.player.get_pos()[1] > ball.get_pos()[1]):
                    self.player.move_arquero(270, ball.get_speed())
        else:
            if(self.player.get_pos()[1] < half_height):
                self.player.move_arquero(90, ball.get_speed())
            elif(self.player.get_pos()[1] > half_height):
                self.player.move_arquero(270, ball.get_speed())
            else:
                self.player.set_speed(0.0)
                self.player.set_angle(self.player.get_fov().get_angle_to_object(self.player.get_team().get_field().get_ball()))
            
    def goal_kick(self):
        self.player.reposition()
        last_touch = self.player.get_team().get_field().get_ball().get_last_touch()
        side = self.player.get_side()
        if (side != last_touch):
            if (side == 0):
                angles = [45, 315]
                random_angle = random.choice(angles)
                time.sleep(0.5)
                self.player.kick_with_angle(random_angle, self.player.get_strength())
                self.player.get_team().get_field().set_state("Playing")
            else:
                angles = [135, 225]
                random_angle = random.choice(angles)
                time.sleep(0.5)
                self.player.kick_with_angle(random_angle, self.player.get_strength())
                self.player.get_team().get_field().set_state("Playing")
        return

class FieldPlayerBehaviour(Behaviour):
    def __init__(self, pos: list[float], forwarding) -> None:
        super().__init__(pos)
        self.forwarding = forwarding
        self.lock = players_lock

    def try_score(self) -> bool:
        if (
            (self.player.get_side() == 0 and self.pos_in_goal_area_rs(self.player.get_pos())) 
            or 
            (self.player.get_side() == 1 and self.pos_in_goal_area_ls(self.player.get_pos()))
        ):
            angle_to_arco = self.player.get_fov().get_angle_to_pos([self.get_arco_line()[0][0], half_height])

            while not self.spin(angle_to_arco):
                pass

            upper_angle = self.player.get_fov().get_angle_to_pos(self.get_arco_line()[0])
            bottom_angle = self.player.get_fov().get_angle_to_pos(self.get_arco_line()[1])

            if(upper_angle > bottom_angle):
                greatest_angle = upper_angle
                least_angle = bottom_angle
            else:
                greatest_angle = bottom_angle
                least_angle = upper_angle

            side = self.player.get_side()
            if side == 0:
                enemy_side = 1
            else:
                enemy_side = 0
            
            teammates = self.player.get_team().get_field().get_players_team(side)
            enemies = self.player.get_team().get_field().get_players_team(enemy_side)
            for i in range(1, len(teammates)):
                enemy = enemies[i]
                my_angle = self.player.get_fov().get_angle_to_object(enemy)
                if(side == 0):
                    if(greatest_angle >= 270) and (my_angle >= greatest_angle):
                        if(least_angle >= 270 and my_angle <= least_angle) or (least_angle <= 270 and my_angle >= least_angle):
                            return False
                    if(greatest_angle >= my_angle >= least_angle) and greatest_angle < 270:
                        return False
            self.player.set_speed(0.0)
            return True
        return False

    def try_move_forward(self) -> bool:
        player_pos = self.player.get_pos()
        if(self.player.get_side() == 0):
            next_move = [player_pos[0] + 5*player_size[0], player_pos[1]]
            if(self.free_path(next_move)):
                self.move_with_ball(self.player.get_fov().get_angle_to_pos(next_move))
                return True
            else:
                next_move = [player_pos[0] - 5*player_size[0], player_pos[1]]
                if(self.free_path(next_move)):
                    self.move_with_ball(self.player.get_fov().get_angle_to_pos(next_move))
                    return True
        else:
            next_move = [player_pos[0] - 5*player_size[0], player_pos[1]]
            if(self.free_path(next_move)):
                self.move_with_ball(self.player.get_fov().get_angle_to_pos(next_move))
                return True
            else:
                next_move = [player_pos[0] + 5*player_size[0], player_pos[1]]
                if(self.free_path([next_move[0], player_pos[1]])):
                    self.move_with_ball(self.player.get_fov().get_angle_to_pos([next_move[0], player_pos[1]]))
                    return True
        return False

    def flow(self):
        if(self.player.get_team().get_field().get_state() == "Playing"):
            ball = self.player.get_team().get_field().get_ball()
            nearest_to_ball = self.player_has_ball()
            if (nearest_to_ball[0] == self.player):
                if(self.try_score()):
                    self.aim_and_kick()
                else:
                    target_pass = self.free_teammate(True)
                    if(target_pass == None):
                        if(not self.try_move_forward()):
                            target_pass = self.free_teammate(False)
                            if target_pass == None:
                                self.hold_ball()
                            else:
                                self.aim_and_pass(target_pass)
                    else:
                        self.aim_and_pass(target_pass) 
            elif (nearest_to_ball[0] != None) and (nearest_to_ball[0].get_side() == self.player.get_side()):
                self.unmark()
            elif (nearest_to_ball[0] != None) and (nearest_to_ball[0].get_side() != self.player.get_side()):
                if(nearest_to_ball[1] == self.player):
                    angle = self.player.get_fov().get_angle_to_object(ball)
                    self.player.move(angle, self.player.get_speed())
                else:
                    self.mark()
            elif (nearest_to_ball[0] == None):
                if(nearest_to_ball[1] == self.player and ball.get_speed() != 0):
                    self.intercept(self.player.get_speed())
                elif (nearest_to_ball[1] == self.player and ball.get_speed() == 0):
                    angle = self.player.get_fov().get_angle_to_object(ball)
                    self.player.move(angle, self.player.get_speed())
                else:
                    self.action_blind()
        elif(self.player.get_team().get_field().get_state() == "Out of Game"):
            self.out_of_game()
        elif(self.player.get_team().get_field().get_state() == "Goal Kick"):
            self.goal_kick()
        else:
            self.score()
             
    def action_blind(self):
        if(self.team_posession()):
            if self.player.get_side() == 0:
                self.player.move(self.player.get_fov().get_angle_to_pos([self.player.get_pos()[0] + self.forwarding, self.player.get_pos()[1]]), self.player.get_speed())
            else:
                self.player.move(self.player.get_fov().get_angle_to_pos([self.player.get_pos()[0] - self.forwarding, self.player.get_pos()[1]]), self.player.get_speed())
        else:
            self.player.move(self.player.get_fov().get_angle_to_pos(self.pos), self.player.get_speed())

    def move_with_ball(self, angle):
        with self.lock:
            self.player.kick_with_angle(angle, 2*self.player.get_speed())
            self.player.move(angle, 0.5*self.player.get_speed())

    def goal_kick(self):
        side = self.player.get_side()
        if (
            (side == 0 and self.pos_in_goal_area_rs(self.player.get_pos())) 
            or 
            (side == 1 and self.pos_in_goal_area_ls(self.player.get_pos()))
        ):
            self.player.move(self.player.get_fov().get_angle_to_pos(self.pos), self.player.get_speed())
        else:
            self.player.set_speed(0)

    def out_of_game(self):
        last_touch = self.player.get_team().get_field().get_ball().get_last_touch()
        nearest = self.player_has_ball()
        ball = self.player.get_team().get_field().get_ball()
        if(nearest[1] == self.player) and (self.player.get_side() != last_touch):
            angle = self.player.get_fov().get_angle_to_object(ball)
            self.player.move(angle, self.player.get_speed())

            if(self.player.get_side() == 0):
                while(self.player.get_pos()[1] < ball.get_pos()[1]):
                    pass
                self.player.set_speed(0.0)
            else:
                while(self.player.get_pos()[1] > ball.get_pos()[1]):
                    pass
                self.player.set_speed(0.0)
            
            self.player.set_speed(0.0)
            pass_forward = self.free_teammate(True)
            pass_backwards = self.free_teammate(False)
            if(pass_forward == None):
                if(pass_backwards == None):
                    self.player.kick_with_angle(self.player.get_fov().get_angle_to_pos([self.arco_line[0][0], half_height]), self.player.get_strength())
                else:
                    self.aim_and_pass(pass_backwards)
            else:
                self.aim_and_pass(pass_forward)    

            self.player.get_team().get_field().set_state("Playing")
        else:
            self.player.move(self.player.get_fov().get_angle_to_object(ball), 0.0)
            
    def score(self):
        team_scored = self.player.get_team().get_field().get_last_score()
        nearest = self.player_has_ball()
        self.player.set_speed(0.0)
        team_side = self.player.get_side()
        if(team_side != team_scored):
            if(nearest[1] == self.player):
                ball = self.player.get_team().get_field().get_ball()
                angle = self.player.get_fov().get_angle_to_object(ball)
                self.player.move(angle, self.player.get_speed())
                
                if(team_side == 0):
                    while(self.player.get_pos()[0] < ball.get_pos()[0]):
                        #print(self.player.get_pos(), " ", ball.get_pos())
                        pass
                else:
                    while(self.player.get_pos()[0] > ball.get_pos()[0]):
                        #print(self.player.get_pos(), " ", ball.get_pos())
                        pass
                
                teammate_list = self.player.get_team().get_players()
                for i in range(1, len(teammate_list)):
                    teammate = teammate_list[i]
                    if (self.player != teammate):
                        self.aim_and_pass(teammate)
                        break
                
                self.player.get_team().get_field().set_state("Playing")

    def ball_taken(self) -> bool: # la tiene el enemigo A SU ALCANCE, NO PUEDO INTERCEPTAR (la veo)
        return False

    def unmark(self):
        side = self.player.get_side()
        pos = self.player.get_pos()
        if(side == 0):
            move_up_right = (pos[0] + 2*player_size[0], pos[1] + 5*player_size[0])
            move_down_right = (pos[0] + 2*player_size[0], pos[1] - 5*player_size[0])
            move_backwards = (pos[0] - 2*player_size[0], pos[1])
            move_forward = (pos[0] + 2*player_size[0], pos[1])
            
            if ((move_forward[0] < self.player.get_team().get_field().rs_goal_area_singleline[0][0])):
                if(self.free_path(move_forward)):
                    self.player.move(self.player.get_fov().get_angle_to_pos(move_forward), self.player.get_speed())
                elif(self.free_path(move_up_right)):
                    self.player.move(self.player.get_fov().get_angle_to_pos(move_up_right), self.player.get_speed())
                elif (self.free_path(move_down_right)):
                    self.player.move(self.player.get_fov().get_angle_to_pos(move_down_right), self.player.get_speed())
            else:
                self.player.move(self.player.get_fov().get_angle_to_pos(move_backwards), self.player.get_speed())
        else:
            move_up_right = (pos[0] - 2*player_size[0], pos[1] + 5*player_size[0])
            move_down_right = (pos[0] - 2*player_size[0], pos[1] - 5*player_size[0])
            move_backwards = (pos[0] + 2*player_size[0], pos[1])
            move_forward = (pos[0] - 2*player_size[0], pos[1])

            if ((move_forward[0] > self.player.get_team().get_field().ls_goal_area_singleline[0][0])):
                if(self.free_path(move_forward)):
                    self.player.move(self.player.get_fov().get_angle_to_pos(move_forward), self.player.get_speed())
                elif(self.free_path(move_up_right)):
                    self.player.move(self.player.get_fov().get_angle_to_pos(move_up_right), self.player.get_speed())
                elif (self.free_path(move_down_right)):
                    self.player.move(self.player.get_fov().get_angle_to_pos(move_down_right), self.player.get_speed())
            else:
                self.player.move(self.player.get_fov().get_angle_to_pos(move_backwards), self.player.get_speed())

    def mark(self):
        side = self.player.get_side()
        pos = self.player.get_pos()
        if(side == 0):
            move_backwards = (pos[0] - 2*player_size[0], half_height)         
            self.player.move(self.player.get_fov().get_angle_to_pos(move_backwards), self.player.get_speed())
        else:
            move_backwards = (pos[0] + 2*player_size[0], half_height)
            self.player.move(self.player.get_fov().get_angle_to_pos(move_backwards), self.player.get_speed())
    
    def search_ball(self) -> bool:
        ball = self.player.get_team().get_field().get_ball()
        angle_to_ball = self.player.get_fov().get_angle_to_object(ball)
        while not self.player.get_fov().is_sprite_at_view(ball):
            self.spin(angle_to_ball)
            if(self.player.get_angle() == angle_to_ball):
                return False

        distance = math.sqrt(((self.player.get_pos()[0] - ball.get_pos()[0])**2 + (self.player.get_pos()[1] - ball.get_pos()[1])**2))
        return distance < 6*player_size[0]

class DefenderBehaviour(FieldPlayerBehaviour):
    def __init__(self, pos: list[float], forwarding) -> None:
        super().__init__(pos, forwarding)
    
    def reject_ball(self):
        side = self.player.get_side()
        pos = self.player.get_pos()
        if(side == 0):
            if(pos[1] < half_height):
                self.player.kick_with_angle(315, self.player.get_strength())
            else:
                self.player.kick_with_angle(45, self.player.get_strength())
        else:
            if(pos[1] < half_height):
                self.player.kick_with_angle(225, self.player.get_strength())
            else:
                self.player.kick_with_angle(135, self.player.get_strength())
        
    def try_move_forward(self) -> bool:
        side = self.player.get_side()
        pos = self.player.get_pos()
        if(side == 0):
            if(pos[0] < half_width):
                return super().try_move_forward()
        else:
            if(pos[0] > half_width):
                return super().try_move_forward()
        return False

    def free_teammate(self, forward_pass: bool) -> Player:
        teammates = self.player.get_team().get_players()
        teammates_at_view = list()
        for i in range(1, len(teammates)):
            teammate = teammates[i]
            if(self.player.get_fov().is_sprite_at_view(teammate)):
                teammates_at_view.append(teammate)
        for free in teammates_at_view:
            if free is not self.player:
                return free
   
    def unmark(self):
        self.player.move(self.player.get_fov().get_angle_to_pos(self.pos), 0.3*self.player.get_speed())

    def mark(self):
        side = self.player.get_side()
        if  side == 0:
            enemy_team = 1
        else:
            enemy_team = 0

        enemies_at_view = list()
        for enemy in self.player.get_team().get_field().get_players_team(enemy_team):
            if(self.player.get_fov().is_sprite_at_view(enemy)):
                enemies_at_view.append(enemy)

        nearest = None
        nearest_distance = 1920

        for enemy in enemies_at_view:
            enemy_distance = math.sqrt(((self.get_pos()[0] - enemy.get_pos()[0])**2 + (self.get_pos()[1] - enemy.get_pos()[1])**2))
            if((nearest == None or enemy_distance < nearest_distance)):
                nearest = enemy
                nearest_distance = enemy_distance
        if (nearest != None):
            self.player.move(self.player.get_fov().get_angle_to_pos(nearest.get_pos()), self.player.get_speed())
        return nearest

    def action_blind(self): 
        self.player.move(self.player.get_fov().get_angle_to_pos(self.pos), 0.3*self.player.get_speed())

    def flow(self):
        if(self.player.get_team().get_field().get_state() == "Playing"):
            ball = self.player.get_team().get_field().get_ball()
            nearest_to_ball = self.player_has_ball()
            if (nearest_to_ball[0] == self.player):
                target_pass = self.free_teammate(True)
                if(target_pass == None):
                    if(not self.try_move_forward()):
                        self.reject_ball()
                else:
                    self.aim_and_pass(target_pass) 
            elif (nearest_to_ball[0] != None) and (nearest_to_ball[0].get_side() == self.player.get_side()):
                self.unmark()
            elif (nearest_to_ball[0] != None) and (nearest_to_ball[0].get_side() != self.player.get_side()):
                if(nearest_to_ball[1] == self.player):
                    angle = self.player.get_fov().get_angle_to_object(ball)
                    self.player.move(angle, self.player.get_speed())
                else:
                    if (self.mark() == None):
                        self.unmark()
            elif (nearest_to_ball[0] == None) and ((self.player.get_side() == 0 and ball.get_pos()[0] < half_width) or (self.player.get_side() == 1 and ball.get_pos()[0] > half_width)):
                if(nearest_to_ball[1] == self.player and ball.get_speed() != 0):
                    self.intercept(self.player.get_speed())
                elif (nearest_to_ball[1] == self.player and ball.get_speed() == 0):
                    angle = self.player.get_fov().get_angle_to_object(ball)
                    self.player.move(angle, self.player.get_speed())
                else:
                    self.action_blind()
        elif(self.player.get_team().get_field().get_state() == "Out of Game"):
            self.out_of_game()
        elif(self.player.get_team().get_field().get_state() == "Goal Kick"):
            self.goal_kick()
        else:
            self.score()

class StrikerBehaviour(FieldPlayerBehaviour):
    def __init__(self, pos: list[float], forwarding, strike_pos: list[float]) -> None:
        super().__init__(pos, forwarding)
        self.strike_pos = strike_pos
        
    def set_pos(self, pos):
        super().set_pos(pos)
        self.strike_pos = [screen_width - self.strike_pos[0], screen_height - self.strike_pos[1]]

    def goal_kick(self):
        side = self.player.get_side()
        if (
            (side == 0 and self.pos_in_goal_area_rs(self.player.get_pos())) 
            or 
            (side == 1 and self.pos_in_goal_area_ls(self.player.get_pos()))
        ):
            self.player.move(self.player.get_fov().get_angle_to_pos(self.pos), self.player.get_speed())
        else:
            self.player.set_speed(0)

    def free_teammate_stk(self) -> Player:
        teammates_at_view = list()
        for teammate in self.player.get_team().get_players():
            if(self.player.get_fov().is_sprite_at_view(teammate)):
                teammates_at_view.append(teammate)
        side = self.player.get_side()
        if  side == 0:
            enemy_team = 1
        else:
            enemy_team = 0

        enemies_at_view = list()
        for enemy in self.player.get_team().get_field().get_players_team(enemy_team):
            if(self.player.get_fov().is_sprite_at_view(enemy)):
                enemies_at_view.append(enemy)

        
        for free in teammates_at_view:
            if free is not self.player:
                for enemy in enemies_at_view:
                    if(abs(self.player.get_fov().get_angle_to_pos(free.get_pos()) - self.player.get_fov().get_angle_to_pos(enemy.get_pos())) < 6):
                        if(side == 0):
                            if(self.player.get_pos()[0] < free.get_pos()[0]):
                                return free
                        else:
                            if(self.player.get_pos()[0] > free.get_pos()[0]):
                                return free

        nearest = None
        nearest_distance = 1920
        for free in teammates_at_view:
            if free is not self.player:
                flag = True
                distance = math.sqrt(((self.get_pos()[0] - free.get_pos()[0])**2 + (self.get_pos()[1] - free.get_pos()[1])**2))
                for enemy in enemies_at_view:
                    if(abs(self.player.get_fov().get_angle_to_pos(free.get_pos()) - self.player.get_fov().get_angle_to_pos(enemy.get_pos())) < 6):
                        enemy_distance = math.sqrt(((self.get_pos()[0] - enemy.get_pos()[0])**2 + (self.get_pos()[1] - enemy.get_pos()[1])**2))
                        if(distance >= enemy_distance):
                            flag = False
                            break
                
                if((nearest == None or distance < nearest_distance) and flag):
                        nearest = free
                        nearest_distance = distance
        if nearest != None: 
            if(self.player.get_pos()[1] != nearest.get_pos()[1]):
                return nearest
        return None
    
    def action_blind(self):
        ball_pos = self.player.get_team().get_field().get_ball().get_pos()
        if (self.player.get_side() == 0):
                if(ball_pos[0] >= half_width):
                    self.player.move(self.player.get_fov().get_angle_to_pos([self.strike_pos[0] + self.forwarding, self.strike_pos[1]]), self.player.get_speed())
                else:
                    self.player.move(self.player.get_fov().get_angle_to_pos([self.strike_pos[0] - self.forwarding, self.strike_pos[1]]), self.player.get_speed())
        else:
            if(ball_pos[0] >= half_width):
                self.player.move(self.player.get_fov().get_angle_to_pos([self.strike_pos[0] - self.forwarding, self.strike_pos[1]]), self.player.get_speed())
            else:
                self.player.move(self.player.get_fov().get_angle_to_pos([self.strike_pos[0] + self.forwarding, self.strike_pos[1]]), self.player.get_speed())
            
    def flow(self):
        if(self.player.get_team().get_field().get_state() == "Playing"):
            ball = self.player.get_team().get_field().get_ball()
            nearest_to_ball = self.player_has_ball()
            if (nearest_to_ball[0] == self.player):
                if(self.try_score()):
                    self.aim_and_kick()
                else:
                    if(not self.try_move_forward()): 
                        target_pass = self.free_teammate_stk()
                        if(target_pass == None):
                            self.player.kick([self.arco_line[0][0], self.arco_line[0][1] + (abs(self.arco_line[1][1] - self.arco_line[0][1]) / 2)], self.player.get_strength())
                        else:
                            self.aim_and_pass(target_pass) 
            elif (nearest_to_ball[0] != None) and (nearest_to_ball[0].get_side() == self.player.get_side()):
                self.unmark()
            elif (nearest_to_ball[0] != None) and (nearest_to_ball[0].get_side() != self.player.get_side()):
                if(nearest_to_ball[1] == self.player):
                    angle = self.player.get_fov().get_angle_to_object(ball)
                    self.player.move(angle, self.player.get_speed())
                else:
                    self.action_blind()
            elif (nearest_to_ball[0] == None):
                if(nearest_to_ball[1] == self.player and ball.get_speed() != 0):
                    self.intercept(self.player.get_speed())
                elif (nearest_to_ball[1] == self.player and ball.get_speed() == 0):
                    angle = self.player.get_fov().get_angle_to_object(ball)
                    self.player.move(angle, self.player.get_speed())
                else:
                    self.action_blind()
        elif(self.player.get_team().get_field().get_state() == "Out of Game"):
            self.out_of_game()
        
        elif(self.player.get_team().get_field().get_state() == "Goal Kick"):
            self.goal_kick()
        else:
            self.score()

class Team:
    def __init__(self, name, goalkeeper, behaviour):
        self.name = name
        self.side = 0
        goalkeeper.set_behaviour(behaviour)
        goalkeeper.set_team(self)
        behaviour.set_player(goalkeeper)
        self.player_list = list()
        self.player_list.append(goalkeeper)

    def set_field(self, field) -> None:
        self.field = field

    def reset_players_speed(self):
        for player in self.player_list:
            player.set_speed(0)

    def get_field(self) -> SoccerField:
        return self.field

    def get_side(self):
        return self.side

    def add_player(self, player, behaviour):
        player.set_team(self)
        player.set_behaviour(behaviour)
        behaviour.set_player(player)
        self.player_list.append(player)

    def get_name(self) -> str:
        return self.name

    def reposition(self):
        for player in self.player_list:
            player.reposition()
        
    def set_side(self, side):
        for player in self.player_list:
            player.set_side(self.side, side)
        self.side = side

    def draw(self):
        for player in self.player_list:
            player.draw()

    def get_side(self):
        return self.side

    def start(self):
        for player in self.player_list:
            player.start()

    def get_player(self, number) -> Player:
        return self.player_list[number]

    def get_players(self) -> list:
        return self.player_list.copy()

##### GAME POSITIONS ########

GK = [screen_width - field_width, half_height]

ST = [half_width - 2.5*player_size[0], half_height]

RW = [ST[0] - player_size[0], ST[1] + 3*player_size[0]]
LW = [ST[0] - player_size[0], ST[1] - 3*player_size[0]]

LB = [LW[0] - 5*player_size[0], LW[1] - 2*player_size[0]]
RB = [RW[0] - 5*player_size[0], RW[1] + 2*player_size[0]]
CB_L = [LB[0], LB[1] + 3*player_size[0]]
CB_R = [RB[0], RB[1] - 3*player_size[0]]

CM_L = [CB_L[0] + 5*player_size[0], CB_L[1] - 2*player_size[0]]
CM_M = [CB_L[0] + 4*player_size[0], ST[1]] 
CM_R = [CB_R[0] + 5*player_size[0], CB_R[1] + 2*player_size[0]]

# arqueros   
goalkeeper = Player("JUNINHO PERNAMBUCANO", 6, 45, p1_gk)
behaviour = GoalkeeperBehaviour(GK)
team_1 = Team("", goalkeeper, behaviour)

player2 = Player("PAQUI", 6, 45, p2_gk)
behaviour2 = GoalkeeperBehaviour(GK)
team_2 = Team("", player2, behaviour2)


# players team 1
t1p1 = Player("t1p1", 6, 25, p2_df)
t1b1 = DefenderBehaviour(LB, 150)
team_1.add_player(t1p1, t1b1)

t1p2 = Player("t1p2", 6, 25, p2_df)
t1b2 = DefenderBehaviour(CB_L, 150)
team_1.add_player(t1p2, t1b2)

t1p3 = Player("t1p3", 6, 25, p2_df)
t1b3 = DefenderBehaviour(CB_R, 150)
team_1.add_player(t1p3, t1b3)

t1p4 = Player("t1p4", 6, 25, p2_df)
t1b4 = DefenderBehaviour(RB, 150)
team_1.add_player(t1p4, t1b4)

t1p5 = Player("t1p5", 6, 25, p2_field)
t1b5 = FieldPlayerBehaviour(CM_L, 200)
team_1.add_player(t1p5, t1b5)

t1p6 = Player("t1p6", 6, 25, p2_field)
t1b6 = FieldPlayerBehaviour(CM_M, 200)
team_1.add_player(t1p6, t1b6)

t1p7 = Player("t1p7", 6, 25, p2_field)
t1b7 = FieldPlayerBehaviour(CM_R, 200)
team_1.add_player(t1p7, t1b7)

t1p8 = Player("t1p8", 6, 25, p2_st)
t1b8 = StrikerBehaviour(LW, 200, [half_width + 0.5*half_width, LW[1]])
team_1.add_player(t1p8, t1b8)

t1p9 = Player("t1p9", 6, 25, p2_st)
t1b9 = StrikerBehaviour(RW, 200, [half_width + 0.5*half_width, RW[1]])
team_1.add_player(t1p9, t1b9)

t1p10 = Player("t1p10", 6, 25, p2_st)
t1b10 = StrikerBehaviour(ST, 200, [half_width + 0.5*half_width, ST[1]])
team_1.add_player(t1p10, t1b10)
'''
class Graph:
    def __init__(self):
        self.graph = {}
        self.lock = threading.Lock()

    def add_edge(self, vertex1, vertex2):
        player1_pos = vertex1.get_pos()
        player2_pos = vertex2.get_pos()
        distance = math.sqrt((player2_pos[0] - player1_pos[0])**2 + (player2_pos[1] - player1_pos[1])**2)
        self.graph[vertex1][vertex2] = distance
        self.graph[vertex2][vertex1] = distance

    def add_vertex(self, vertex):
        if vertex not in self.graph:
            self.graph[vertex] = {}

    def display(self):
        for vertex, neighbors in self.graph.items():
            neighbors_str = ', -> '.join([f"{neighbor.get_name()}: {weight:.2f}" for neighbor, weight in neighbors.items()])
            print(f"Player {vertex.get_name()} -> {neighbors_str}")

    def get_mid_weight_neighbor(self, player):
        with self.lock:
            neighbors = self.graph[player]
            if neighbors:
                sorted_neighbors = sorted(neighbors, key=lambda x: self.graph[player][x])
                mid_index = len(sorted_neighbors) // 2
                return sorted_neighbors[mid_index]

    def get_min_weight_edge(self, player):
        with self.lock:
            neighbors = [neighbor for neighbor in self.graph[player].keys() if neighbor != player]
            closest_neighbor = min(neighbors, key=lambda x: self.graph[player][x])
            return closest_neighbor


    def update_weights(self, player):
        with self.lock:
            new_pos = player.get_pos()
            for other_player, distance in self.graph[player].items():
                updated_distance = math.sqrt((new_pos[0] - other_player.get_pos()[0])**2 + (new_pos[1] - other_player.get_pos()[1])**2)
                self.graph[player][other_player] = updated_distance
                self.graph[other_player][player] = updated_distance

    def set_all(self):
        with self.lock:
            vertexs = list(self.graph.keys())
            for i in range(len(vertexs)):
                for j in range(i + 1, len(vertexs)):
                    self.add_edge(vertexs[i], vertexs[j])

class CorchoDefender(DefenderBehaviour):
    def __init__(self, pos: list[float], forwarding, team_graph, marked_enemies) -> None:
        super().__init__(pos, forwarding)
        self.graph = team_graph
        self.current_behavior = None
        self.marked_enemies = marked_enemies

    def set_player(self, player):
        super().set_player(player)
        self.graph.add_vertex(self.player)

    def nearest_enemy(self):
        if self.player.side == 0:
            enemy_side = 1
        else:
            enemy_side = 0
        enemies = self.player.get_team().get_field().get_players_team(enemy_side)

        nearest_distance = 1920
        nearest_enemy = None
        player_pos = self.player.get_pos()
        for enemy in enemies:
            distance_enemy = math.sqrt(((player_pos[0] - enemy.get_pos()[0])**2 + (player_pos[1]  - enemy.get_pos()[1])**2))
            if(distance_enemy < nearest_distance):
                nearest_distance = distance_enemy
                nearest_enemy = enemy
        
        return nearest_enemy

    def mark_enemy(self, target):
        if self.player.side == 0:
            enemy_side = 1
        else:
            enemy_side = 0
        if target not in self.marked_enemies:
            return target
        else:
            for enemy in self.player.get_team().get_field().get_players_team(enemy_side):
                if enemy not in self.marked_enemies or not self.marked_enemies[enemy]:
                    self.marked_enemies[enemy] = True
                    return enemy
        return None

    def update(self):
        self.graph.update_weights(self.player)

    def free_teammate(self, forward_pass:bool) -> Player:
        return self.graph.get_mid_weight_neighbor(self.player)
        #return self.graph.get_min_weight_edge(self.player)

    def change_behaviour(self, ball):
        if self.player.get_side() == 0:
            if ball.get_pos()[0] > half_width :
                new_b = CorchoFieldPlayer(self.pos, self.forwarding, self.graph, self.marked_enemies)
                new_b.set_player(self.player)
                self.player.set_behaviour(new_b)
                return
        else:
            if ball.get_pos()[0] < half_width:
                new_b = CorchoFieldPlayer(self.pos, self.forwarding, self.graph, self.marked_enemies)
                new_b.set_player(self.player)
                self.player.set_behaviour(new_b)
                return

    def flow(self):
        self.change_behaviour(self.player.get_team().get_field().get_ball())
        if(self.player.get_team().get_field().get_state() == "Playing"):
            ball = self.player.get_team().get_field().get_ball()
            nearest_to_ball = self.player_has_ball()
            if (nearest_to_ball[0] == self.player):
                target_pass = self.free_teammate(True)
                if(target_pass == None):
                    if(not self.try_move_forward()):
                        self.reject_ball()
                else:
                    self.aim_and_pass(target_pass) 
            elif (nearest_to_ball[0] != None) and (nearest_to_ball[0].get_side() == self.player.get_side()):
                self.unmark()
            elif (nearest_to_ball[0] != None) and (nearest_to_ball[0].get_side() != self.player.get_side()):
                if(nearest_to_ball[1] == self.player):
                    angle = self.player.get_fov().get_angle_to_object(ball)
                    self.player.move(angle, self.player.get_speed())
                else:
                    if (self.mark() == None):
                        self.unmark()
            elif (nearest_to_ball[0] == None) and ((self.player.get_side() == 0 and ball.get_pos()[0] < half_width) or (self.player.get_side() == 1 and ball.get_pos()[0] > half_width)):
                if(nearest_to_ball[1] == self.player and ball.get_speed() != 0):
                    self.intercept(self.player.get_speed())
                elif (nearest_to_ball[1] == self.player and ball.get_speed() == 0):
                    angle = self.player.get_fov().get_angle_to_object(ball)
                    self.player.move(angle, self.player.get_speed())
                else:
                    self.action_blind()
        elif(self.player.get_team().get_field().get_state() == "Out of Game"):
            self.out_of_game()
        elif(self.player.get_team().get_field().get_state() == "Goal Kick"):
            self.goal_kick()
        else:
            self.score()
        self.update()

class CorchoFieldPlayer(FieldPlayerBehaviour):
    def __init__(self, pos: list[float], forwarding, team_graph, marked_enemies) -> None:
        super().__init__(pos, forwarding)
        self.graph = team_graph
        self.current_behavior = None
        self.marked_enemies = marked_enemies
        
    def set_player(self, player):
        super().set_player(player)
        self.graph.add_vertex(self.player)

    def update(self):
        self.graph.update_weights(self.player)

    def free_teammate(self, forward_pass:bool) -> Player:
        return self.graph.get_min_weight_edge(self.player)

    def change_behaviour(self, ball):
        if self.player.get_side() == 0:
            if ball.get_pos()[0] < half_width :
                new_b = CorchoDefender(self.pos, self.forwarding, self.graph, self.marked_enemies)
                new_b.set_player(self.player)
                self.player.set_behaviour(new_b)
                return
        else:
            if ball.get_pos()[0] > half_width:
                new_b = CorchoDefender(self.pos, self.forwarding, self.graph, self.marked_enemies)
                new_b.set_player(self.player)
                self.player.set_behaviour(new_b)
                return

    def flow(self):
        if(self.player.get_team().get_field().get_state() == "Playing"):
            ball = self.player.get_team().get_field().get_ball()
            self.change_behaviour(ball)
            nearest_to_ball = self.player_has_ball()
            if (nearest_to_ball[0] == self.player): 
                if(self.try_score()):
                    self.aim_and_kick()
                else:
                    target_pass = self.free_teammate(True)
                    if(not self.player.get_fov().is_sprite_at_view(target_pass)):
                        if(not self.try_move_forward()):

                            self.aim_and_pass(target_pass) 
            elif (nearest_to_ball[0] != None) and (nearest_to_ball[0].get_side() == self.player.get_side()):
                self.unmark()
            elif (nearest_to_ball[0] != None) and (nearest_to_ball[0].get_side() != self.player.get_side()):
                if(nearest_to_ball[1] == self.player):
                    angle = self.player.get_fov().get_angle_to_object(ball)
                    self.player.move(angle, self.player.get_speed())
                else:
                    self.mark()
            elif (nearest_to_ball[0] == None):
                if(nearest_to_ball[1] == self.player and ball.get_speed() != 0):
                    self.intercept(self.player.get_speed())
                elif (nearest_to_ball[1] == self.player and ball.get_speed() == 0):
                    angle = self.player.get_fov().get_angle_to_object(ball)
                    self.player.move(angle, self.player.get_speed())
                else:
                    self.action_blind()
        elif(self.player.get_team().get_field().get_state() == "Out of Game"):
            self.out_of_game()
        elif(self.player.get_team().get_field().get_state() == "Goal Kick"):
            self.goal_kick()
        else:
            self.score()
        self.update()

    def action_blind(self):
        if self.player.get_side() == 0:
            self.player.move(self.player.get_fov().get_angle_to_pos([self.pos[0] + self.forwarding, self.pos[1]]), self.player.get_speed())
        else:
            self.player.move(self.player.get_fov().get_angle_to_pos([self.pos[0] - self.forwarding, self.pos[1]]), self.player.get_speed())

class CorchoStriker(StrikerBehaviour):
    def __init__(self, pos: list[float], forwarding, strike_pos: list[float], team_graph) -> None:
        super().__init__(pos, forwarding, strike_pos)
        self.graph = team_graph

    def set_player(self, player):
        super().set_player(player)
        self.graph.add_vertex(self.player)

    def update(self):
        self.graph.update_weights(self.player)

    def free_teammate_stk(self) -> Player:
        return self.graph.get_min_weight_edge(self.player)

    def flow(self):
        if(self.player.get_team().get_field().get_state() == "Playing"):
            ball = self.player.get_team().get_field().get_ball()
            nearest_to_ball = self.player_has_ball()
            if (nearest_to_ball[0] == self.player):
                if(self.try_score()):
                    self.aim_and_kick()
                else:
                    if(not self.try_move_forward()): 
                        target_pass = self.free_teammate_stk()
                        if(not self.player.get_fov().is_sprite_at_view(target_pass)):
                            self.player.kick([self.arco_line[0][0], self.arco_line[0][1] + (abs(self.arco_line[1][1] - self.arco_line[0][1]) / 2)], self.player.get_strength())
                        else:
                            self.aim_and_pass(target_pass) 
            elif (nearest_to_ball[0] != None) and (nearest_to_ball[0].get_side() == self.player.get_side()):
                self.unmark()
            elif (nearest_to_ball[0] != None) and (nearest_to_ball[0].get_side() != self.player.get_side()):
                if(nearest_to_ball[1] == self.player):
                    angle = self.player.get_fov().get_angle_to_object(ball)
                    self.player.move(angle, self.player.get_speed())
                else:
                    self.action_blind()
            elif (nearest_to_ball[0] == None):
                if(nearest_to_ball[1] == self.player and ball.get_speed() != 0):
                    self.intercept(self.player.get_speed())
                elif (nearest_to_ball[1] == self.player and ball.get_speed() == 0):
                    angle = self.player.get_fov().get_angle_to_object(ball)
                    self.player.move(angle, self.player.get_speed())
                else:
                    self.action_blind()
        elif(self.player.get_team().get_field().get_state() == "Out of Game"):
            self.out_of_game()
        elif(self.player.get_team().get_field().get_state() == "Goal Kick"):
            self.goal_kick()
        else:
            self.score()
        self.update()


grafolol = Graph()
behaviourArquero = GoalkeeperBehaviour(GK)
marked_enemies = dict()
behaviourC1 = CorchoDefender(LB, 100, grafolol, marked_enemies)
behaviourC4 = CorchoDefender(RB, 100, grafolol, marked_enemies)
behaviourC2 = CorchoDefender(CB_L, 200, grafolol, marked_enemies)
behaviourC3 = CorchoDefender(CB_R, 100, grafolol, marked_enemies)
behaviourC5 = CorchoFieldPlayer(CM_L, 200, grafolol, marked_enemies)
behaviourC6 = CorchoFieldPlayer(CM_M, 200, grafolol, marked_enemies)
behaviourC7 = CorchoFieldPlayer(CM_R, 200, grafolol, marked_enemies)
behaviourC8 = CorchoStriker(LW, 200, [half_width + 0.5*half_width, LW[1]], grafolol)
behaviourC9 = CorchoStriker(RW, 200, [half_width + 0.5*half_width, RW[1]], grafolol)
behaviourC10 = CorchoStriker(ST, 200, [half_width + 0.5*half_width, ST[1]], grafolol)
corcho1 = Player("Corcho1", 6, 25, p1_df)
corcho2 = Player("Corcho2", 6, 25, p1_df)
corcho3 = Player("Corcho3", 6, 25, p1_df)
corcho4 = Player("Corcho4", 6, 25, p1_df)
corcho5 = Player("Corcho5", 6, 25, p1_field)
corcho6 = Player("Corcho6", 6, 25, p1_field)
corcho7 = Player("Corcho7", 6, 25, p1_field)
corcho8 = Player("Corcho8", 6, 25, p1_st)
corcho9 = Player("Corcho9", 6, 25, p1_st)
corcho10 = Player("Corcho10", 6, 25, p1_st)
team_2.add_player(corcho1, behaviourC1)
team_2.add_player(corcho2, behaviourC2)
team_2.add_player(corcho3, behaviourC3)
team_2.add_player(corcho4, behaviourC4)
team_2.add_player(corcho5, behaviourC5)
team_2.add_player(corcho6, behaviourC6)
team_2.add_player(corcho7, behaviourC7)
team_2.add_player(corcho8, behaviourC8)
team_2.add_player(corcho9, behaviourC9)
team_2.add_player(corcho10, behaviourC10)
grafolol.add_vertex(player2)
grafolol.set_all()

'''

# players team 2

t2p1 = Player("t2p1", 6, 25, p1_df)
t2b1 = DefenderBehaviour(LB, 150)
team_2.add_player(t2p1, t2b1)

t2p2 = Player("t2p2", 6, 25, p1_df)
t2b2 = DefenderBehaviour(CB_L, 150)
team_2.add_player(t2p2, t2b2)

t2p3 = Player("t2p3", 6, 25, p1_df)
t2b3 = DefenderBehaviour(CB_R, 150)
team_2.add_player(t2p3, t2b3)

t2p4 = Player("t2p4", 6, 25, p1_df)
t2b4 = DefenderBehaviour(RB, 150)
team_2.add_player(t2p4, t2b4)

t2p5 = Player("t2p5", 6, 25, p1_field)
t2b5 = FieldPlayerBehaviour(CM_L, 200)
team_2.add_player(t2p5, t2b5)

t2p6 = Player("t2p6", 6, 25, p1_field)
t2b6 = FieldPlayerBehaviour(CM_M, 200)
team_2.add_player(t2p6, t2b6)

t2p7 = Player("t2p7", 6, 25, p1_field)
t2b7 = FieldPlayerBehaviour(CM_R, 200)
team_2.add_player(t2p7, t2b7)

t2p8 = Player("t2p8", 6, 25, p1_st)
t2b8 = StrikerBehaviour(LW, 200, [half_width + 0.5*half_width, LW[1]])
team_2.add_player(t2p8, t2b8)

t2p9 = Player("t2p9", 6, 25, p1_st)
t2b9 = StrikerBehaviour(RW, 200, [half_width + 0.5*half_width, RW[1]])
team_2.add_player(t2p9, t2b9)

t2p10 = Player("t2p10", 6, 25, p1_st)
t2b10 = StrikerBehaviour(ST, 200, [half_width + 0.5*half_width, ST[1]])
team_2.add_player(t2p10, t2b10)

field = SoccerField(team_1, team_2, [0,0])
team_1.set_field(field)
team_2.set_field(field)




start_time = pygame.time.get_ticks()
first_set = True

field.begin()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    
    
    field.draw()
    team_1.draw()
    team_2.draw()
    field.get_ball().draw()
    field.throw_in()
    field.goal()
    field.palo()
    field.corner()
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    current_time = f"{minutes:02d}:{seconds:02d}"

    if current_time == "01:00" and first_set:
        field.change_gametime()
        first_set = False
    time_surface = font.render(current_time, True, (255, 255, 255))
    screen.blit(time_surface, (int(field.middle_line[0][0] - (5*font_size/6)), int(field.top_left_corner[1]/2) - (font_size)))

    clock.tick(30)  
    pygame.display.flip()