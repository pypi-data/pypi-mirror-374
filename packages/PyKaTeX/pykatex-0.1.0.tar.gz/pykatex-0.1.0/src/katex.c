#include "quickjs-libc.h"
#include "katex.bytecode.h"

#include "katex.h"

#define MAX_NUM_ARGS 2
#define MAX_JS_VALUES 128

typedef struct {
	bool initialized;
	JSRuntime *runtime;
	JSContext *context;
	JSValue renderToString;
	JSValue js_options;
	JSValue js_values[MAX_JS_VALUES];
	int num_js_values;
	JSException exception;
	bool has_exception;
} KatexState;

static KatexState state = {
	.initialized = false,
	.runtime = NULL,
	.context = NULL,
	.num_js_values = 0,
	.has_exception = false,
};

static void state_initialize(KatexState *state);
static void state_finalize(KatexState *state);
char *state_renderToString(KatexState *state, const char *input, const KatexOptions *c_options);
JSException *state_get_last_js_error(KatexState *state);

JSValue build_js_options(KatexState *state, const KatexOptions *c_options);
static void free_option_values(KatexState *state, JSValue js_options);
static void set_bool_option(KatexState *state, const char *key, const bool *value);
static void set_number_option(KatexState *state, const char *key, const double *value);
static void set_string_option(KatexState *state, const char *key, const char *value);

void katex_initialize(void) {
	state_initialize(&state);
}

char *katex_renderToString(const char *input, KatexOptions *c_options) {
	return state_renderToString(&state, input, c_options);
}

JSException *katex_get_last_error(void) {
	return state_get_last_js_error(&state);
}

void katex_finalize(void) {
	state_finalize(&state);
}

static void state_initialize(KatexState *state) {
	JSRuntime *runtime = JS_NewRuntime();
	js_std_init_handlers(runtime);
	JS_SetModuleLoaderFunc(runtime, NULL, js_module_loader, NULL);

	JSContext *context = JS_NewContextRaw(runtime);
	JS_AddIntrinsicBaseObjects(context);
	JS_AddIntrinsicRegExp(context);
	JS_AddIntrinsicJSON(context);
	JS_AddIntrinsicPromise(context);

	js_std_eval_binary(context, qjsc_katex, qjsc_katex_size, 1);
	js_std_add_helpers(context, 0, 0);
	js_std_eval_binary(context, katex, katex_size, 0);

	JSValue global = JS_GetGlobalObject(context);
	JSValue renderToString = JS_GetPropertyStr(context, global, "renderToString");

	state->runtime = runtime;
	state->context = context;
	state->renderToString = renderToString;
	state->num_js_values = 0;
	state->has_exception = false;
	state->initialized = true;

	JS_FreeValue(state->context, global);
}

static void state_finalize(KatexState *state) {
	JS_FreeValue(state->context, state->renderToString);
	free_option_values(state, state->js_options);

	js_std_free_handlers(state->runtime);
	JS_FreeContext(state->context);
	JS_FreeRuntime(state->runtime);

	if (state->has_exception) {
		JS_FreeCString(state->context, state->exception.name);
		JS_FreeCString(state->context, state->exception.message);
		state->has_exception = false;
	}

	state->initialized = false;
}

char *state_renderToString(KatexState *state, const char *input, const KatexOptions *c_options) {
	if (!state->initialized) {
		katex_initialize();
	}

	JSValue js_input = JS_NewStringLen(state->context, input, strlen(input));
	JSValue js_options;
	
	int num_args = 1;
	if (c_options) {
		num_args++;
		js_options = build_js_options(state, c_options);
	}

	JSValue args[MAX_NUM_ARGS] = { js_input, js_options };

	JSValue js_result = JS_Call(state->context, state->renderToString, JS_UNDEFINED, num_args, args);
	JS_FreeValue(state->context, js_input);

	if (c_options) {
		JS_FreeValue(state->context, js_options);
		free_option_values(state, js_options);
	}

	if (JS_IsException(js_result)) {
		JS_FreeValue(state->context, js_result);
		return NULL;
	}

	const char *c_result = JS_ToCString(state->context, js_result);
	JS_FreeValue(state->context, js_result);

	if (c_result == NULL) {
		return NULL;
	}

	size_t len = strlen(c_result) + 1;
	char *result = malloc(len);
	memcpy(result, c_result, len);

	JS_FreeCString(state->context, c_result);

	return result;
}

JSException *state_get_last_js_error(KatexState *state) {
	if (state->has_exception) {
		JS_FreeCString(state->context, state->exception.name);
		JS_FreeCString(state->context, state->exception.message);
		state->has_exception = false;
	}

	JSValue exception = JS_GetException(state->context);
	if (JS_IsUndefined(exception)) {
		return NULL;
	} else {
		JSAtom name_atom = JS_NewAtom(state->context, "name");
		JSAtom message_atom = JS_NewAtom(state->context, "message");
		if (JS_HasProperty(state->context, exception, name_atom) && JS_HasProperty(state->context, exception, message_atom)) {
			JSValue js_name = JS_GetProperty(state->context, exception, name_atom);
			JSValue js_message = JS_GetProperty(state->context, exception, message_atom);
			state->exception.name = JS_ToCString(state->context, js_name);
			state->exception.message = JS_ToCString(state->context, js_message);
			JS_FreeValue(state->context, js_name);
			JS_FreeValue(state->context, js_name);
			state->has_exception = true;
		}
		JS_FreeAtom(state->context, name_atom);
		JS_FreeAtom(state->context, message_atom);
	}

	return state->has_exception ? &state->exception : NULL;
}

JSValue build_js_options(KatexState *state, const KatexOptions *c_options) {
	state->js_options = JS_NewObject(state->context);

	set_bool_option(state, "displayMode", c_options->display_mode);
	set_string_option(state, "output", c_options->output);
	set_bool_option(state, "leqno", c_options->leqno);
	set_bool_option(state, "fleqn", c_options->fleqn);
	set_bool_option(state, "throwOnError", c_options->throw_on_error);
	set_string_option(state, "errorColor", c_options->error_color);
	// TODO: macros
	set_number_option(state, "minRuleThickness", c_options->min_rule_thickness);
	set_bool_option(state, "colorIsTextColor", c_options->color_is_text_color);
	set_number_option(state, "maxSize", c_options->max_size);
	set_number_option(state, "maxExpand", c_options->max_expand);
	set_bool_option(state, "strict", c_options->strictBool);
	set_string_option(state, "strict", c_options->strictStr);
	set_bool_option(state, "trust", c_options->trust);
	set_bool_option(state, "globalGroup", c_options->global_group);

	return state->js_options;
}

static void free_option_values(KatexState *state, JSValue js_options) {
	for (int i = 0; i < state->num_js_values; i++) {
		JS_FreeValue(state->context, state->js_values[i]);
	}
	state->num_js_values = 0;
}

static void set_bool_option(KatexState *state, const char *key, const bool *value) {
	if (value) {
		JSValue option = JS_NewBool(state->context, *value);
		state->js_values[state->num_js_values++] = option;
		JS_SetPropertyStr(state->context, state->js_options, key, option);
	}
}

static void set_number_option(KatexState *state, const char *key, const double *value) {
	if (value) {
		JSValue option = JS_NewFloat64(state->context, *value);
		state->js_values[state->num_js_values++] = option;
		JS_SetPropertyStr(state->context, state->js_options, key, option);
	}
}

static void set_string_option(KatexState *state, const char *key, const char *value) {
	if (value) {
		JSValue option = JS_NewString(state->context, value);
		JS_SetPropertyStr(state->context, state->js_options, key, option);
	}
}
