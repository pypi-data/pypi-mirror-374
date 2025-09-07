#ifndef KATEX_H
#define KATEX_H

#include <stdbool.h>

typedef struct {
  const bool *display_mode;
  const char *output;
  const bool *leqno;
  const bool *fleqn;
  const bool *throw_on_error;
  const char *error_color;
  // TODO: macros
  const double *min_rule_thickness;
  const bool *color_is_text_color;
  const double *max_size;
  const double *max_expand;
  const bool *strictBool;
  const char *strictStr;
  const bool *trust;
  const bool *global_group;
} KatexOptions;

typedef struct {
	const char *name;
	const char *message;
} JSException;

void katex_initialize(void);
char *katex_renderToString(const char *input, KatexOptions *options);
JSException *katex_get_last_error(void);
void katex_finalize(void);

#endif
