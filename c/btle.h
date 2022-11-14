#define BTLE_CONNECT  0
#define BTLE_CLICK_BUTTON 1
#define BTLE_CLICK_SELECT 2
#define BTLE_CLICK_TEXT 3
#define SERVER_TIMER    4
#define BTLE_DISCONNECT 5
#define SERVER_START 6
#define BTLE_CLICK_CHECK 7
#define BTLE_BROADCAST 8

#define BTLE_CONTINUE 0
#define BTLE_EXIT     1

#define FONT_DEFAULT 0
#define FONT_THIN    1
#define FONT_LIGHT   2
#define FONT_MEDIUM  3
#define FONT_THICK   4
#define FONT_CONDENSED 5
#define FONT_FIXED   6
#define FONT_SERIF   7
#define FONT_SERIF_FIXED 8
#define FONT_CASUAL  9
#define FONT_DANCING 10
#define FONT_GOTHIC  11
#define FONT_MAX 11

#define STYLE_FILL 0
#define STYLE_STROKE 1
#define DIRN_HORIZ 0
#define DIRN_VERT  1

#define DEFAULT_VALUE 255
#define NO_CHANGE  254

#define CLOCK_SHORT 0
#define CLOCK_LONG 1
#define ANTICLOCK_SHORT 2
#define ANTICLOCK_LONG 3

#define LINE_BREAK -32768
#define POINTS_OFF 0
#define POINTS_SQUARE 1
#define POINTS_CIRCLE 2
#define POINTS_CROSS 3
#define POINTS_TRIANGLE 4
#define POINTS_ONLY 128

#define UNCHECKED 0
#define CHECKED 1

char *btle_address(int device);

int btle_broadcast(char *mess);
int btle_button(int device,char *text);

int btle_change_check(int device,int handle,int state);
int btle_change_colour(int device,int handle,int red,int green,int blue);
int btle_change_font(int device,int handle,int font);
int btle_change_text(int device,int handle,char *text);
int btle_check(int device,int state);
int btle_clear(int device);
int btle_connected(int device);
int btle_connect_settings(int device,int tos,int retry);

int btle_disconnect(int device);

int btle_font(int device,int font);

int *btle_handles(void);

int btle_image(int device,int width,int height,int numlines,int red,int green,int blue);
int btle_image_arc(int device,int handle,int x0,int y0,int x1,int y1,int radius,int route,int width,int red,int green,int blue);
int btle_image_circle(int device,int handle,int x0,int y0,int radius,int red,int green,int blue,int style,int wid);
int btle_image_clear(int device,int handle);
int btle_image_line(int device,int handle,int x0,int y0,int x1,int y1,int width,int red,int green,int blue);
int btle_image_multiline(int device,int handle,int *x,int *y,int start,int end,int width,int red,int green,int blue,int pstyle,int pwid);
int btle_image_oval(int device,int handle,int x0,int y0,int x1,int y1,int red,int green,int blue,int style,int wid);
int btle_image_rect(int device,int handle,int x0,int y0,int x1,int y1,int red,int green,int blue,int style,int wid);
int btle_image_text(int device,int handle,char *text,int x0,int y0,int dirn,int font,int size,int red,int green,int blue);

char *btle_local_address();
char *btle_local_name();

int btle_maxdevice(void);
int btle_message(int device,char *mess);  
int btle_message_all(char *mess);  
int btle_message_buffer(int device,int bufsz);

char *btle_name(int device);
int btle_newline(int device);

int btle_password(char *pword);

int btle_remove(int device,int handle);
int btle_restore(int device,int handle);

int btle_scale_data(float *x,float *y,int start,int end,float xmin,float xmax,float ymin,float ymax,
               int originx,int originy,int toprx,int topry,int *px,int *py,int len);
int btle_select(int device,char *text);
int btle_server(int(*callback)(),char *name);
int btle_server_ex(int(*callback)(),char *name,int hci);
int btle_slave(void);
int btle_spacings(int device,int hpad,int vpad,int hspace,int vspace);

int btle_text(int device,char *text);
int btle_text_input(int device,int width);
int btle_timer(int timerds);





