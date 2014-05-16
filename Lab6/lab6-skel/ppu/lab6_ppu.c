/*
 * Computer System Architecture - Lab 6
 * PPU code
 */

#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <libspe2.h>
#include <pthread.h>

extern spe_program_handle_t lab6_spu;

#define MAX_SPU_THREADS   16


typedef struct {
	int id;
} parameter;


void *ppu_pthread_function(void *arg) {
// void *ppu_pthread_function() {

	parameter *p=(parameter *)arg;
	spe_context_ptr_t ctx;

	/* Create SPE context */

	if ((ctx = spe_context_create (0, NULL)) == NULL) {
		perror ("Failed creating context");
		exit (1);
	}

	/* Load SPE program into context */

	if (spe_program_load (ctx, &lab6_spu)) {
		perror ("Failed loading program");
		exit (1);
	}


	/* Run SPE context */

	unsigned int entry = SPE_DEFAULT_ENTRY;
	if (spe_context_run(ctx, &entry, 0, p->id, NULL, NULL) < 0) {
	// if (spe_context_run(ctx, &entry, 0, NULL, NULL, NULL) < 0) {
		perror ("Failed running context");
		exit (1);
	}

	/* Destroy context */

	if (spe_context_destroy (ctx) != 0) {
		perror("Failed destroying context");
		exit (1);
	}

	pthread_exit(NULL);
}

int main()
{

	int n = spe_cpu_info_get(SPE_COUNT_USABLE_SPES, -1);
	pthread_t thread;
	int i;
	parameter *p;
	p=(parameter *)malloc(sizeof(parameter)*n);


	/* am comentat ca sa ruleze doar 1 thread*/


	/* Create thread for each SPE context */
	// for(i = 0; i< n ;i++){
		if (pthread_create (&thread, NULL, &ppu_pthread_function, (void *)(p+0)))  {
		// if (pthread_create (&thread[i], NULL, &ppu_pthread_function, NULL))  {
			perror ("Failed creating thread");
			exit (1);
		}
	// }

	// for(i = 0; i< n ;i++){
	/* Wait for SPU-thread to complete execution.  */
		if (pthread_join (thread, NULL)) {
			perror("Failed pthread_join");
			exit (1);
		}
	// }


	printf("\nThe program has successfully executed.\n");
	return 0;
}