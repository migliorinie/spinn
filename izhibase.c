#include<math.h>
#include<stdio.h>
#include<stdlib.h>

#include<time.h>

#include<fcntl.h>
#include<unistd.h>

// Including the header causes problems, so I'm prototyping here.
double mt_drand();
void mt_seed();

void intPrintMat(int mat[], int width, int height) {
    for(int j = 0; j<height; j++) {
        for(int i = 0; i<width; i++) {
            printf("%d, ", mat[i+j*width]);
        }
        printf("\n");
    }
}

void doublePrintMat(double mat[], int width, int height, int to_file) {
    if(to_file == 0) {
        for(int j = 0; j<height; j++) {
            for(int i = 0; i<width; i++) {
                printf("%f, ", mat[i+j*width]);
            }
            printf("\n");
        }
    } else {
        FILE* fp = fopen("C_log_test.txt", "w+");
        for(int j = 0; j<height; j++) {
            for(int i = 0; i<width; i++) {
                fprintf(fp, "%f ", mat[i+j*width]);
            }
        }
    }
}

void symPrintMat(int mat[], int width, int height) {
    for(int j = 0; j<height; j++) {
        for(int i = 0; i<width; i++) {
            printf(mat[i+j*width] == 1 ? "#" : ".");
        }
        printf("\n");
    }
}

double BMRandom() {
    // Box-Mueller. If I feel lucky, mtwist also has a random dist file.
    double U = mt_drand();
    double V = mt_drand();
    return sqrt(-2*log(U))*cos(6.283*V);
}

// Helper function to print to BMP the firings. In B/W
void bmpPrintMat(int mat[], int width, int height, char* filename) {
    int fd = open(filename, O_WRONLY|O_CREAT|O_TRUNC, S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH|S_IWOTH);
    static unsigned char header[54] = {66,77,0,0,0,0,0,0,0,0,54,0,0,0,40,0,0,0,0,0,0,0,0,0,0,0,1,0,24};
    unsigned int pixelBytesPerRow = width*3*sizeof(char);
    unsigned int paddingBytesPerRow = (4-(pixelBytesPerRow%4))%4;
    unsigned int* sizeOfFileEntry = (unsigned int*) &header[2];
    *sizeOfFileEntry = 54+(pixelBytesPerRow+paddingBytesPerRow)*height;
    unsigned int* widthEntry = (unsigned int*) &header[18];
    *widthEntry = width;
    unsigned int* heightEntry = (unsigned int*) &header[22];
    *heightEntry = height;
    write(fd, header, 54);
    static unsigned char zeroes[3] = {0,0,0};
    for (int row = 0; row<height; row++) {
        for (int col = 0; col<width; col++) {
            unsigned char pix[3] = {255*(1-mat[col+row*width]), 255*(1-mat[col+row*width]), 255*(1-mat[col+row*width])};
            write(fd, pix, 3*sizeof(char));
        }
        write(fd, zeroes, paddingBytesPerRow);
    }
    close(fd);
}

// This first version goes with 100 neurons. If it works, I'll make it better.
int main(int argc, char* argv[]) {
    
    clock_t beginTime = clock();
    
    const int Ne = 800;
    const int Ni = 200;
    const int timesteps = 1000;
    const int sampleNeuron = 96;
    
    //1 to activate Ambroise-Levi, 0 to switch it off
    int ALon = 1;
    double ALnorm = 1.0 - 0.21875*ALon;
    
    mt_seed();
    time_t t;
    srand((unsigned) time(&t));

    /*double sample100[100] = {0.67268635, 0.96309749, 0.55220653, 0.89180605, 0.23468753, 0.81446299, 0.02195218, 0.83865616, 0.32659993, 0.24142225, 0.25734255, 0.91201752, 0.76794863, 0.23790365, 0.98089552, 0.92428144, 0.21600643, 0.83424292, 0.69386298, 0.46489522, 0.014518, 0.01957745, 0.7461725, 0.46113239, 0.61514745, 0.92841833, 0.08349969, 0.95070375, 0.58733038, 0.19839871, 0.25190411, 0.56569044, 0.6211112, 0.92418393, 0.72089119, 0.36120168, 0.25103747, 0.77158686, 0.71478856, 0.89871678, 0.90135932, 0.7473526, 0.22538937, 0.51225528, 0.56152225, 0.93567016, 0.63801067, 0.95226071, 0.73292152, 0.18399366, 0.1024284, 0.99834277, 0.56280422, 0.01583075, 0.06538782, 0.4483554, 0.99148011, 0.01410149, 0.81852111, 0.8343277, 0.93690884, 0.99741748, 0.29923517, 0.79460516, 0.51615389, 0.14538083, 0.04862664, 0.62384621, 0.59551652, 0.9189782, 0.89446678, 0.49094778, 0.18917208, 0.3231677, 0.34190464, 0.7116547, 0.49402238, 0.2225873, 0.15917861, 0.73371542, 0.69298251, 0.57648452, 0.64508938, 0.42175717, 0.62483895, 0.36801571, 0.76858529, 0.31535117, 0.009977 , 0.46877673, 0.94155195, 0.20507172, 0.52609205, 0.36366941, 0.76585519, 0.94148786, 0.42066063, 0.06366899, 0.43467719, 0.05397984};*/
    double *sample = (double*)malloc((Ne+Ni)*sizeof(double));
    for (int i = 0; i<(Ne+Ni); i++) {
        sample[i] = mt_drand();
        //sample[i] = ((double)rand()/RAND_MAX);
    }

    double *aVec = (double*)malloc((Ne+Ni)*sizeof(double));
    double *bVec = (double*)malloc((Ne+Ni)*sizeof(double));
    double *cVec = (double*)malloc((Ne+Ni)*sizeof(double));
    double *dVec = (double*)malloc((Ne+Ni)*sizeof(double));
    
    // A-Z variables
    double *k1 = (double*)malloc((Ne+Ni)*sizeof(double));
    double k2 = -62.5; // Formula for the X of the vertex of 0.04v^2 + 5v + 140
    double *k3 = (double*)malloc((Ne+Ni)*sizeof(double));

    // Horizontally divided into Ne and Ni
    double *sMat = (double*)malloc((Ne+Ni)*(Ne+Ni)*sizeof(double));

    double *vVec = (double*)malloc((Ne+Ni)*sizeof(double));
    double *uVec = (double*)malloc((Ne+Ni)*sizeof(double));

    int *firings = (int*)malloc((Ne+Ni)*timesteps*sizeof(int));
    double *sampleVTracer = (double*)malloc(timesteps*sizeof(double));

    // Initialization
    for (int i = 0; i<Ne; i++){
        double re = sample[i];
        aVec[i] = 0.02;
        bVec[i] = 0.2;
        cVec[i] = -65+15*re*re;
        dVec[i] = 8-6*re*re;
        
        // Ahmadi-Zwolinski: I did my calculations on a piece of paper, let's see if it works. b[i] MUST be nonzero.
        //k1[i] = sqrt(pow(bVec[i],2)-10.0*bVec[i]+2.6);
        //k3[i] = 12.5*(pow(bVec[i],2)-5.0*bVec[i]-abs(pow(bVec[i],2)-10.0*bVec[i]+2.6));
        k1[i] = 0.8;
        k3[i] = -12.0;

        vVec[i] = -65;
        uVec[i] = bVec[i]*vVec[i];
        for(int j = 0; j<(Ne+Ni); j++) {
            sMat[i+j*(Ne+Ni)] = 0.5*mt_drand();
            //sMat[i+j*(Ne+Ni)] = 0.5*((double)rand()/RAND_MAX);
        }
    }

    for (int i = Ne; i<(Ne+Ni); i++){
        double ri = sample[i];
        aVec[i] = 0.02+0.08*ri;
        bVec[i] = 0.25-0.05*ri;
        cVec[i] = -65;
        dVec[i] = 2;
        
        // Ahmadi-Zwolinski: I did my calculations on a piece of paper, let's see if it works. b[i] MUST be nonzero.
        //k1[i] = sqrt(pow(bVec[i],2)-10.0*bVec[i]+2.6);
        //k3[i] = 12.5*(pow(bVec[i],2)-5.0*bVec[i]-abs(pow(bVec[i],2)-10.0*bVec[i]+2.6));
        // Using the averages
        k1[i] = 0.6227249;
        k3[i] = -13.4336546;

        vVec[i] = -65;
        uVec[i] = bVec[i]*vVec[i];
        for(int j = 0; j<(Ne+Ni); j++) {
            sMat[i+j*(Ne+Ni)] = -1*mt_drand();
            //sMat[i+j*(Ne+Ni)] = -1*((double)rand()/RAND_MAX);
        }
    }
    
    //doublePrintMat(sMat, Ne+Ni, Ne+Ni);
    double *iVec = (double*)malloc((Ne+Ni)*sizeof(double));
    // Boolean hack definition?
    int *fired = (int*)malloc((Ne+Ni)*sizeof(int));
    
    //doublePrintMat(k1, Ne+Ni, 1);
    //doublePrintMat(k3, Ne+Ni, 1);
    
    clock_t preProcTime = clock();
    printf("Time spent pre-processing: %f cycles\n", (double)(preProcTime-beginTime));
    // Double SHOULD be enough. If it's not, long double.
    clock_t prevTime = preProcTime;
    double* iterTimeVec = (double*)malloc(timesteps*sizeof(double));
    double* neuronTimeVec = (double*)malloc((Ne+Ni)*timesteps*sizeof(double));
    
    for(int step = 0; step<timesteps; step++) {
        sampleVTracer[step] = vVec[sampleNeuron];
        double sumVec[Ne+Ni];
        for(int j = 0; j<(Ne+Ni); j++) {
            sumVec[j] = 0;
        }
        for(int i = 0; i<(Ne+Ni); i++) {
            iVec[i] = (i < Ne ? 5 : 2)*BMRandom();
            fired[i] = vVec[i] > 30.0*ALnorm ? 1 : 0;
            firings[step * (Ne + Ni) + i] = fired[i];

            if (fired[i] == 1) {
                vVec[i] = cVec[i];
                uVec[i] += dVec[i];
                for (int j = 0; j < Ne + Ni; j++) {
                    sumVec[j] += sMat[i + j * (Ne + Ni)];
                }
            }
        }
        for(int i = 0; i<(Ne+Ni); i++) {
            clock_t firsterm = clock();
            iVec[i] = iVec[i] + sumVec[i]*ALnorm;
            // 1) iVec can be split into several parts to simulate the Ambroise-Levi currents;
            // 2) Further lowering sumVec changes behavior somehow.
            
            // Izhikevic
            //vVec[i] = vVec[i]+0.5*(0.04*pow(vVec[i], 2)+5*vVec[i]+140-uVec[i]+iVec[i]);
            //vVec[i] = vVec[i]+0.5*(0.04*pow(vVec[i], 2)+5*vVec[i]+140-uVec[i]+iVec[i]);
            
            // Ambroise-Levi
            vVec[i] = vVec[i]+ALnorm*(0.04*pow(vVec[i], 2)+5*vVec[i]+140-uVec[i])+iVec[i];
            
            // Ahmadi-Zwolinski
            //vVec[i] = vVec[i] + k1[i]*abs(vVec[i]-k2)+k3[i]-uVec[i]+iVec[i];
            
            // Always the same
            uVec[i] = uVec[i]+aVec[i]*(bVec[i]*vVec[i]-uVec[i]);
            neuronTimeVec[step*timesteps+i] = (double)(clock()-firsterm);
        }
        clock_t tstamp = clock();
        iterTimeVec[step] = (double)(tstamp-prevTime);
        prevTime = tstamp;
    }
    printf("Time spent elaborating: %f cycles\n", (double)(prevTime-preProcTime));
    printf("Time spent since beginning: %f cycles\n", (double)(prevTime-beginTime));
    
    double averagedIter = 0;
    double averagedNeuron = 0;
    for (int i = 0; i < timesteps; i++) {
        averagedIter += iterTimeVec[i];
        for(int j = 0; j < (Ne+Ni); j++) {
            averagedNeuron += neuronTimeVec[i*timesteps+j];
        }
    }
    averagedIter /= timesteps;
    averagedNeuron /= (timesteps*(Ne+Ni));
    printf("Average time for an iteration: %f cycles\n", averagedIter);
    printf("Average time for a neuron: %f cycles\n", averagedNeuron);
    
    printf("Elaboration done. Saving...\n");
    bmpPrintMat(firings, Ne+Ni, timesteps, argc > 1 ? argv[1] : "primo.bmp");
    //symPrintMat(firings, Ne+Ni, timesteps);
    //doublePrintMat(sampleVTracer, timesteps, 1, 1);
    doublePrintMat(neuronTimeVec, (Ne+Ni)*timesteps, 1, 1);
    
}