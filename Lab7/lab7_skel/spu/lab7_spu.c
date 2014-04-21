/* alexandru.olteanu@cs.pub.ro, 31/03/2014 */

#include <stdio.h>
#include <spu_intrinsics.h>
#include <spu_mfcio.h>

#define SIZE 32000
#define CHUNKS 80
#define CHUNK_SIZE SIZE/CHUNKS

int main(unsigned long long speid){

		uint32_t valoare = 1337;
		uint32_t val = 0;
		uint32_t sum = 0;
		uint32_t i;

		unsigned int data[SIZE] __attribute__((aligned(16)));
		unsigned int buffer[CHUNK_SIZE/2] __attribute__((aligned(16)));

		for (i=0; i<SIZE; i++) {
				//data[i] = i%100 * ((i/100)%2==0?1:-1);
				data[i] = 1;
		};

		//TODO: Task3 - inconjoara Task1 si Task2 cu o bucla ca procesarea sa se faca pana la primirea de SPU a unei valori > CHUNKS

		uint32_t mbox_data; // variabila in care se citeste data din mailbox

		while(1){
			while (spu_stat_in_mbox()<=0); // busy-waiting...
			// daca aveam ceva de facut in acest timp, unde scriam codul corespunzator?
			mbox_data = spu_read_in_mbox();
			printf("[SPU %d] received data=%d.Processing...\n", (int) speid, (int)mbox_data);

			if(mbox_data>79){
				printf("[SPU %d] Job done...\n", (int) speid);
				break;
			}

			while(1){
				if (spu_stat_out_mbox() > 0) {
					printf("[SPU %d] sending data=%d ...\n", (int) speid, (int)mbox_data);
					spu_write_out_mbox((uint32_t) mbox_data);
					break;
				} else {
					printf("Mailbox full.Retrying...\n");
				}
			}


		}

		 sum = 0;
		 if (val<=CHUNKS) {

				 //TODO: Task4 - adunati vectorial prima jumatate a chunk-ului cu a doua jumatate si puneti rezultatul in buffer

		 }

			 //TODO: Task2 - trimite un intreg de la SPU la PPU




		return 0;
}



