
/* Conway's Game of Life
 *  -|- John Andersen (sea_wulf) -|-
 *  -|- Late July 2017           -|-
 *
 * Optimized for memory use, and not graphical output or speed
 *
 * If I had wanted to optimize for speed, then I could have generated a
 *  masking lookup table for every possible combination byte. Also, I could
 *  have held a neighbor count and compressed 3 cells into a half-word so that
 *  you have:
 *      ,_______________________________,
 *      |E|A|B|C|a|b|c|X|X|X|Y|Y|Y|Z|Z|Z|
 *      '```````````````````````````````'
 *
 *      where E is an edge flag, a, b, and c are the current gens cells, A, B, and C
 *      are the previous generations cells, and XXX, YYY, ZZZ are neighbor counts 
 *      (you only need 3 bits because there is an implicit neighbor in the half-word).
 *
 *  And then index the lookup table by the previous state of the half-word. BUT, again,
 *  this is optimized for memory (and arbitrary size parameters).
 *  
 * So, the minimum requirements for memory are max(cells) * 2 + sizeof(size_t) * 2.
 * 
 * That being said, I could probably cut down on the instructions by using bit masks
 *  for specific cases instead of employing a crap-ton of shifts.life.c
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <string.h>

#define TIMEOUT 100

/* Assumes windows or unix-based system. 
 * If you are on some random-ass PowerPC based architecture 
 * then the gods have forsaken you. */ 

#if defined _WIN32 || defined _WIN64
#include <windows.h>

int term_width(HANDLE std_out) {
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    if (std_out == NULL) {
        std_out = GetStdHandle(STD_OUTPUT_HANDLE);
    }
    GetConsoleScreenBufferInfo(std_out, &csbi);
    return (csbi.srWindow.Right - csbi.srWindow.Left + 1);
}

int term_height(HANDLE std_out) {
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    if (std_out == NULL) {
        std_out = GetStdHandle(STD_OUTPUT_HANDLE);
    }
    GetConsoleScreenBufferInfo(std_out, &csbi);
    return (csbi.srWindow.Bottom - csbi.srWindow.Top + 1);
}

void cls(HANDLE hConsole ) {
    COORD coordScreen = { 0, 0 };    /* here's where we'll home the
                                        cursor */ 
    DWORD cCharsWritten;
    CONSOLE_SCREEN_BUFFER_INFO csbi; /* to get buffer info */ 
    DWORD dwConSize;                 /* number of character cells in
                                        the current buffer */ 

    /* get the number of character cells in the current buffer */ 
    GetConsoleScreenBufferInfo( hConsole, &csbi );
    dwConSize = csbi.dwSize.X * csbi.dwSize.Y;

    /* fill the entire screen with blanks */ 
    FillConsoleOutputCharacter(hConsole, (TCHAR) ' ',
                                          dwConSize, coordScreen,
                                          &cCharsWritten );

    /* get the current text attribute */ 
    GetConsoleScreenBufferInfo(hConsole, &csbi );

    /* now set the buffer's attributes accordingly */ 
    FillConsoleOutputAttribute(hConsole, csbi.wAttributes,
                                          dwConSize, coordScreen,
                                          &cCharsWritten );

    /* put the cursor at (0, 0) */ 
    SetConsoleCursorPosition( hConsole, coordScreen );
}

/* There is some weird console level mojo jojo going on
*  So it is advisable that the everything is normalized after
*  calling for the STD_OUTPUT_HANDLE. Or not. I honestly have
*  no idea how Windoze is handling this. */
void move(int x, int y, HANDLE std_out) {
    COORD coords = {x, y};
    if (std_out == NULL) {
        std_out = GetStdHandle(STD_OUTPUT_HANDLE);
    }
    SetConsoleCursorPosition(std_out, coords);
}

int positionx(HANDLE std_out) {
    COORD coords = {0, 0};
    SMALL_RECT rect = {0, 0, 0, 0};
    CONSOLE_SCREEN_BUFFER_INFO lp = { coords, coords, 0, rect, coords};
    if (std_out == NULL) std_out = GetStdHandle(STD_OUTPUT_HANDLE);
    GetConsoleScreenBufferInfo(std_out, &lp);
    return lp.dwCursorPosition.X;
}

int positiony(HANDLE std_out) {
    COORD coords = {0, 0};
    SMALL_RECT rect = {0, 0, 0, 0};
    CONSOLE_SCREEN_BUFFER_INFO lp = { coords, coords, 0, rect, coords};
    if (std_out == NULL) std_out = GetStdHandle(STD_OUTPUT_HANDLE);
    GetConsoleScreenBufferInfo(std_out, &lp);
    return lp.dwCursorPosition.Y;
}

void clear(int x, int y, HANDLE std_out) {
    if (std_out == NULL) std_out = GetStdHandle(STD_OUTPUT_HANDLE);
    if ((x != 0) || (y != 0)) {
        int max_y = term_height(std_out);
        int max_x = term_width(std_out);
        int iterx = x;
        int itery = y;

        while (max_y - itery > 0) {
            while (max_x - iterx > 0) {
                move(iterx, itery, std_out);
                putchar(' ');
                iterx++;
            }
            itery++;
        }
        move(x, y, std_out);
    } else {
        cls(std_out);
    }
}

void sleep(int x) {
    Sleep(x);
}

#else
#include <sys/ioctl.h>
#include <unistd.h>

int term_width(void) {
    struct winsize max;
    ioctl(0, TIOCGWINSZ, &max);
    return max.ws_col;
}

int term_height(void) {
    struct winsize max;
    ioctl(0, TIOCGWINSZ, &max);
    return max.ws_row;
}

void move(int x, int y) {
    printf("\033[%d;%dH", x, y);
}

void clear(int x, int y) {
    printf("\033[H\033[J");
}



#endif


typedef struct gen {
    size_t height;
    size_t width;
    uint8_t *cells;
} gen;


static char *help_printer = "\
A version of Conway's Game of Life. Not particularly optimized, but at least kind of cross-platform.\n\
    [[ Don't try running this on a Commodore64 or Z80 ]]\n\
\n\
Options:\n\
    -m          Runs the Game of Life in the maximum terminal size\n\
    H W         Runs the Game of Life in the specified size\n\
                    H is the integer height of the arena\n\
                    W is the integer width of the arena\n\
    H W -p      Runs the Game of Life in the specified size in place\n";



void* live(gen *lives, uint8_t *prev_state) {
    size_t max = lives->height * lives->width;
    if (prev_state == NULL) {
        free(prev_state);
        return NULL;
    }
    for (int j=0; j < (max / 8) + 1; j++) {
        prev_state[j] = lives->cells[j];
    }

    size_t i = 0;
    uint8_t cell_val = 0;

    while (i < max) {
        for (int j=0; j < lives->width; j++) {
            if (i == 0) { /* Top case */
                if (j == 0) {
                    cell_val = (((prev_state[0] >> 1) & 0x01) +  /* right */
                                ((prev_state[(lives->width - 1) / 8] >> ((lives->width - 1) % 8)) & 0x01) +  /* left */
                                ((prev_state[(max - lives->width) / 8] >> ((max - lives->width) % 8)) & 0x01) +  /* top */
                                ((prev_state[(lives->width) / 8] >> ((lives->width) % 8)) & 0x01) +  /* bot */
                                ((prev_state[(lives->width + 1) / 8] >> ((lives->width + 1) % 8)) & 0x01) + /* bot right */
                                ((prev_state[(2 * lives->width - 1) / 8] >> ((2 * lives->width - 1) % 8)) & 0x01) +  /* bot left */
                                ((prev_state[(max - lives->width + 1) / 8] >> ((max - lives->width + 1) % 8)) & 0x01) +  /* top right */
                                ((prev_state[(max - 1) / 8] >> ((max - 1) % 8)) & 0x01));  /* top left */

                } else if (j == (lives->width - 1)) {
                    cell_val = ((prev_state[0] & 0x01) +  /* right */
                                ((prev_state[(lives->width - 2) / 8] >> ((lives->width - 2) % 8)) & 0x01) +  /* left */
                                ((prev_state[(max - 1) / 8] >> ((max - 1) % 8)) & 0x01) +  /* top */
                                ((prev_state[(2 * lives->width - 1) / 8] >> ((2 * lives->width - 1) % 8)) & 0x01) +  /* bot */
                                ((prev_state[(2 * lives->width - 2) / 8] >> ((2 * lives->width - 2) % 8)) & 0x01) +  /* bot left */
                                ((prev_state[(max - lives->width) / 8] >> ((max - lives->width) % 8)) & 0x01) +  /* top right */
                                ((prev_state[(max - 2) / 8] >> ((max - 2) % 8)) & 0x01));  /* top left */

                } else {
                    cell_val = (((prev_state[(j + 1) / 8] >> ((j + 1) % 8)) & 0x01) +  /* right */
                                ((prev_state[(j - 1) / 8] >> ((j - 1) % 8)) & 0x01) +  /* left */
                                ((prev_state[(j + max - lives->width ) / 8] >> ((j + max - lives->width) % 8)) & 0x01) +  /* top */
                                ((prev_state[(j + lives->width) / 8] >> ((j + lives->width) % 8)) & 0x01) +  /* bot */
                                ((prev_state[(j + lives->width + 1) / 8] >> ((j + lives->width + 1) % 8)) & 0x01) +  /* bot right */
                                ((prev_state[(j + lives->width - 1) / 8] >> ((j + lives->width - 1) % 8)) & 0x01) + /* bot left */
                                ((prev_state[(j + max - lives->width + 1) / 8] >> ((j + max - lives->width + 1) % 8)) & 0x01) +  /* top right */
                                ((prev_state[(j + max - lives->width - 1) / 8] >> ((j + max - lives->width - 1) % 8)) & 0x01));  /* top left */

                }
            } else if ((i + lives->width) == max) { /* bottom case */
                if (j == 0) {
                    cell_val = (((prev_state[(i + 1) / 8] >> ((i + 1) % 8)) & 0x01) +  /* right */
                                ((prev_state[(max - 1) / 8] >> ((max - 1) % 8)) & 0x01) +  /* left */
                                ((prev_state[(i - lives->width) / 8] >> ((i - lives->width) % 8)) & 0x01) +  /* top */
                                (prev_state[0] & 0x01) +  /* bot */
                                ((prev_state[(i - lives->width + 1) / 8] >> ((i - lives->width + 1) % 8)) & 0x01) +  /* top right */
                                ((prev_state[(i - 1) / 8] >> ((i + j - lives->width + 1) % 8)) & 0x01) + /* top left */
                                ((prev_state[(i - lives->width + 1) / 8] >> ((i - lives->width + 1) % 8)) & 0x01) +  /* top right */
                                ((prev_state[0] >> 1) & 0x01) +  /* bot right */
                                ((prev_state[(lives->width - 1) / 8] >> ((lives->width - 1) % 8)) & 0x01));  /* bot left */

                } else if (j == (lives->width - 1)) {
                    cell_val = (((prev_state[i / 8]  >> (i % 8)) & 0x01) +  /* right */
                                ((prev_state[(max - 1) / 8] >> ((max - 1) % 8)) & 0x01) +  /* left */
                                ((prev_state[(i - 1) / 8] >> ((i - 1) % 8)) & 0x01) +  /* top */
                                ((prev_state[j / 8] >> (j % 8)) & 0x01) +  /* bot */
                                ((prev_state[lives->width / 8] >> (lives->width % 8)) & 0x01) +  /* bot right */
                                ((prev_state[(lives->width - 2) / 8] >> ((lives->width - 2) % 8)) & 0x01) +  /* bot left */
                                ((prev_state[(i - lives->width) / 8] >> ((i - lives->width) % 8)) & 0x01) +  /* top right */
                                ((prev_state[(i - 1) / 8] >> ((i - 1) % 8)) & 0x01));  /* top left */

                } else {
                    cell_val = (((prev_state[(i + j + 1) / 8] >> ((i + j + 1) % 8)) & 0x01) +  /* right */
                                ((prev_state[(i + j - 1) / 8] >> ((i + j - 1) % 8)) & 0x01) +  /* left */
                                ((prev_state[(i + j - lives->width) / 8] >> ((i + j - lives->width) % 8)) & 0x01) +  /* top */
                                ((prev_state[j / 8] >> (j % 8)) & 0x01) +  /* bot */
                                ((prev_state[(j + 1) / 8] >> ((j + 1) % 8)) & 0x01) +  /* bot right */
                                ((prev_state[(j - 1) / 8] >> ((j - 1) % 8)) & 0x01) +  /* bot left */
                                ((prev_state[(i + j - lives->width + 1) / 8] >> ((i + j - lives->width + 1) % 8)) & 0x01) +  /* top right */
                                ((prev_state[(i + j - lives->width - 1) / 8] >> ((i + j - lives->width - 1) % 8)) & 0x01));  /* top left */

                }
            } else { /* middle case [in the middle of the block or on the left or right] */
                if (j == 0) { /* left side case */
                    cell_val = (((prev_state[(i + 1) / 8] >> ((i + 1) % 8)) & 0x01) +  /* right */
                                ((prev_state[(i + lives->width - 1) / 8] >> ((i + lives->width - 1) % 8)) & 0x01) +  /* left */
                                ((prev_state[(i - lives->width) / 8] >> ((i - lives->width) % 8)) & 0x01) +  /* top */
                                ((prev_state[(i + lives->width) / 8] >> ((i + lives->width) % 8)) & 0x01) +  /* bot */
                                ((prev_state[(i + lives->width + 1) / 8] >> ((i + lives->width + 1) % 8)) & 0x01) +  /* bot right */
                                ((prev_state[(i + 2 * lives->width - 1) / 8] >> ((i + 2 * lives->width - 1) % 8)) & 0x01) +  /* bot left */
                                ((prev_state[(i - lives->width + 1) / 8] >> ((i - lives->width + 1) % 8)) & 0x01) + /* top right */
                                ((prev_state[(i - 1) / 8] >> ((i - 1) % 8)) & 0x01));  /* top left */

                } else if (j == (lives->width - 1)) { /* right side case */ 
                    cell_val = (((prev_state[i / 8] >> (i % 8)) & 0x01) +  /* right */
                                ((prev_state[(i + lives->width - 2) / 8] >> ((i + lives->width - 2) % 8)) & 0x01) +  /* left */
                                ((prev_state[(i - 1) / 8] >> ((i - 1) % 8)) & 0x01) +  /* top */
                                ((prev_state[(i + 2 * lives->width - 1) / 8] >> ((i + 2 * lives->width - 1) % 8)) & 0x01) +  /* bot */
                                ((prev_state[(i + 2 * lives->width - 2) / 8] >> ((i + 2 * lives->width - 2) % 8)) & 0x01) +  /* bot left */
                                ((prev_state[(i + lives->width) / 8] >> ((i + lives->width) % 8)) & 0x01) +  /* bot right */
                                ((prev_state[(i - 2) / 8] >> ((i - 2) % 8)) & 0x01) + /* top left */
                                ((prev_state[(i - lives->width) / 8] >> ((i - lives->width) % 8)) & 0x01));  /* top right */

                } else { /* Generic case [middle of block] */
                    cell_val = (((prev_state[(i + j + 1) / 8] >> ((i + j + 1) % 8)) & 0x01) +  /* right */
                                ((prev_state[(i + j - 1) / 8] >> ((i + j - 1) % 8)) & 0x01) +  /* left */
                                ((prev_state[(i + j - lives->width) / 8] >> ((i + j - lives->width) % 8)) & 0x01) +  /* top */
                                ((prev_state[(i + j + lives->width) / 8] >> ((i + j + lives->width) % 8)) & 0x01) +  /* bot */
                                ((prev_state[(i + j + lives->width + 1) / 8] >> ((i + j + lives->width + 1) % 8)) & 0x01) +  /* bot right */
                                ((prev_state[(i + j + lives->width - 1) / 8] >> ((i + j + lives->width - 1) % 8)) & 0x01) +  /* bot left */
                                ((prev_state[(i + j - lives->width + 1) / 8] >> ((i + j - lives->width + 1) % 8)) & 0x01) +  /* top right */
                                ((prev_state[(i + j - lives->width - 1) / 8] >> ((i + j - lives->width + 1) % 8)) & 0x01));  /* top left */

                }
            }

            switch (cell_val) {
                case 2:
                    break;
                case 3:
                    if (!((prev_state[(i + j) / 8] >> ((i + j) % 8)) & 0x01)) { /* orig */
                        lives->cells[(i+j) / 8] |= (1 << ((i + j) % 8));
                    }
                    break;
                default:
                    lives->cells[(i+j) / 8] &=  ~(1 << ((i + j) % 8));
                    break;
            }
        }
        i += lives->width;
    }
    return lives;
}

void printer(gen *lives) {
    for (int i=0; i < (lives->height * lives->width); i += lives->width) {
        for (int j=0; j < lives->width; j++) {
            if (lives->cells[(i + j) / 8] >> ((i + j) % 8) & 0x01) {
                putchar('#');
            } else {
                putchar(' ');
            }
        }
        putchar('\n');
    }
}

#if defined _WIN32 || _WIN64
void state_printer(gen *lives, uint8_t *prev, int off_x, int off_y, HANDLE std_out) {
#else
void state_printer(gen *lives, uint8_t *prev, int off_x, int off_y) {
#endif
    for (int i=0; i < (lives->height * lives->width); i += lives->width) {
        for (int j=0; j < lives->width; j++) {
            if ((lives->cells[(i + j) / 8] >> ((i + j) % 8) & 0x01) ^
                (prev[(i + j) / 8] >> ((i + j) % 8) & 0x01)) {
#if defined _WIN32 || _WIN64
                move(j + off_x, i / lives->width + off_y, std_out);
#else
                move(j + off_x, i / lives->width + off_y);
#endif
                if (lives->cells[(i + j) / 8] >> ((i + j) % 8) & 0x01) {
                    putchar('#');
                } else {
                    putchar(' ');
                }
            }
        }
    }
}

/* Returns 1 for alive, 0 for dead */
int _check(gen *lives) {
    int flag = 0;
    for (int i=0; i < ((lives->height * lives->width) / 8 + 1); i++) {
        if (lives->cells[i] > 0) {
            flag = 1;
        }
    }
    return flag;
}


int main(int argv, char *argc[]) {
    char ret = 0;
    int offsetx = 0;
    int offsety = 0;
#if defined _WIN32 || _WIN64
    HANDLE std_out = GetStdHandle(STD_OUTPUT_HANDLE);
    size_t max_w = (size_t) term_width(std_out);
    size_t max_h = (size_t) term_height(std_out);
#else
    size_t max_w = (size_t) term_width();
    size_t max_h = (size_t) term_height();
#endif

    size_t h = 16;
    size_t w = 32;

    switch (argv) {
        case 4:
            if ((argc[3][0] == '-') && (argc[3][1] == 'p')) {
#if defined _WIN32 || _WIN64
                offsety = positiony(std_out) + 1; // Never defined for unix
#else
                offsety = positiony() + 1; // Also, what happened to positionx?
#endif
            } else goto help;

        case 3:
            h = (size_t) strtol(argc[1], NULL, 10);
            if (h > max_h) {
                h = max_h;
            }

            w = (size_t) strtol(argc[2], NULL, 10);
            if (w > max_w) {
                w = max_w;
            }
            break;

        case 2:
            if ((argc[1][0] == '-') && (argc[1][1] == 'm')) {
                h = max_h - 1;
                w = max_w - 1;
            } else goto help;
            break;
        default:
help:
            printf("%s", help_printer);
            goto quitout;
            break;
    }

    srand(time(NULL));

    gen *generation = malloc(sizeof(size_t) + sizeof(size_t) + sizeof(uint8_t *));
    if (generation == NULL) {
        puts("There was an allocation error in creating the first generation");
        ret = 1;
        goto genallocerror;
    }

    generation->height = h;
    generation->width = w;
    generation->cells = malloc(((h * w) / 8) + 1);

    if (generation->cells == NULL) {
        puts("There was an allocation error in creating the previous generation");
        ret = 1;
        goto gencellallocerror;
    }

    uint8_t *previous = malloc(((h * w) / 8) + 1);
    if (previous == NULL) {
        puts("There was an allocation error in creating the previous generation");
        ret = 1;
        goto prevallocerror;
    }

    int limit = 100;
    while (limit) {
        for (int i = 0; i < (((h * w) / 8) + 1); i++) {
            generation->cells[i] = (uint8_t) (rand() % 256);
        }

#if defined _WIN32 || _WIN64
        clear(offsetx, offsety, std_out);
#else
        clear(offsetx, offsety);
#endif
        printer(generation);

        int j = 0;
        while (_check(generation) && (++j < TIMEOUT)) {
            if (live(generation, previous) == NULL) break;
            sleep(16);
#if defined _WIN32 || _WIN64
            state_printer(generation, previous, offsetx, offsety, std_out);
#else
            state_printer(generation, previous, offsetx, offsety);
#endif
        }
        limit -= 1;
    }

#if defined _WIN32 || _WIN64
    clear(offsetx, offsety, std_out);
    CloseHandle(std_out);
#else
    clear(offsetx, offsety);
#endif
    puts("");

prevallocerror:
    free(previous);

gencellallocerror:
    free(generation->cells);

genallocerror:
    free(generation);

quitout:
    return ret;
}
