#include<math.h>
#include<stdio.h>
#include<stdlib.h>
#include<time.h>
#include<fcntl.h>
#include<unistd.h>

void intPrintMat(int mat[], int width, int height) {
    for(int j = 0; j<height; j++) {
        for(int i = 0; i<width; i++) {
            printf("%d ", mat[i+j*width]);
        }
        printf("\n");
    }
}
void doublePrintMat(double mat[], int width, int height) {
    for(int j = 0; j<height; j++) {
        for(int i = 0; i<width; i++) {
            printf("%f ", mat[i+j*width]);
        }
        printf("\n");
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

// Helper function to print to BMP the firings
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

// This first version goes with 100 neurons over 100 milliseconds. If it works, I'll make it better.
int main() {
    const int Ne = 80;
    const int Ni = 20;
    const int timesteps = 500;
    const int sampleNeuron = 96;

    double sample100[100] = {0.67268635, 0.96309749, 0.55220653, 0.89180605, 0.23468753, 0.81446299, 0.02195218, 0.83865616,
                             0.32659993, 0.24142225, 0.25734255, 0.91201752, 0.76794863, 0.23790365, 0.98089552, 0.92428144,
                             0.21600643, 0.83424292, 0.69386298, 0.46489522, 0.014518, 0.01957745, 0.7461725, 0.46113239,
                             0.61514745, 0.92841833, 0.08349969, 0.95070375, 0.58733038, 0.19839871, 0.25190411, 0.56569044,
                             0.6211112, 0.92418393, 0.72089119, 0.36120168, 0.25103747, 0.77158686, 0.71478856, 0.89871678,
                             0.90135932, 0.7473526, 0.22538937, 0.51225528, 0.56152225, 0.93567016, 0.63801067, 0.95226071,
                             0.73292152, 0.18399366, 0.1024284, 0.99834277, 0.56280422, 0.01583075, 0.06538782, 0.4483554,
                             0.99148011, 0.01410149, 0.81852111, 0.8343277, 0.93690884, 0.99741748, 0.29923517, 0.79460516,
                             0.51615389, 0.14538083, 0.04862664, 0.62384621, 0.59551652, 0.9189782, 0.89446678, 0.49094778,
                             0.18917208, 0.3231677, 0.34190464, 0.7116547, 0.49402238, 0.2225873, 0.15917861, 0.73371542,
                             0.69298251, 0.57648452, 0.64508938, 0.42175717, 0.62483895, 0.36801571, 0.76858529, 0.31535117,
                             0.009977 , 0.46877673, 0.94155195, 0.20507172, 0.52609205, 0.36366941, 0.76585519, 0.94148786,
                             0.42066063, 0.06366899, 0.43467719, 0.05397984};

    double aVec[Ne+Ni];
    double bVec[Ne+Ni];
    double cVec[Ne+Ni];
    double dVec[Ne+Ni];

    // Horizontally divided into Ne and Ni
    double sMat[(Ne+Ni)*(Ne+Ni)];

    double vVec[Ne+Ni];
    double uVec[Ne+Ni];

    int firings[(Ne+Ni)*timesteps];
    double sampleVTracer[timesteps];

    time_t t;
    srand((unsigned) time(&t));

    // Initialization
    for (int i = 0; i<Ne; i++){
        double re = sample100[i];
        aVec[i] = 0.02;
        bVec[i] = 0.2;
        cVec[i] = -65+15*re*re;
        dVec[i] = 8-6*re*re;

        vVec[i] = -65;
        uVec[i] = bVec[i]*vVec[i];
        for(int j = 0; j<(Ne+Ni); j++) {
            sMat[i+j*(Ne+Ni)] = 0.5;//*((double)rand()/RAND_MAX);
        }
    }

    for (int i = Ne; i<(Ne+Ni); i++){
        double ri = sample100[i];
        aVec[i] = 0.02+0.08*ri;
        bVec[i] = 0.25-0.05*ri;
        cVec[i] = -65;
        dVec[i] = 2;

        vVec[i] = -65;
        uVec[i] = bVec[i]*vVec[i];
        for(int j = 0; j<(Ne+Ni); j++) {
            sMat[i+j*(Ne+Ni)] = -1;//*((double)rand()/RAND_MAX);
        }
    }
    //printf("Initialized vectors and matrices\n");

    //doublePrintMat(sMat, Ne+Ni, Ne+Ni);
    double iVec[Ne+Ni];
    // Boolean hack definition? todo
    int fired[Ne+Ni];
    for(int step = 0; step<timesteps; step++) {
        // Need a better randomizer
        sampleVTracer[step] = vVec[sampleNeuron];
        double sumVec[Ne+Ni];
        for(int j = 0; j<(Ne+Ni); j++) {
            sumVec[j] = 0;
        }
        for(int i = 0; i<(Ne+Ni); i++) {
            iVec[i] = sample100[i] * (i < Ne ? 5 : 2);
            fired[i] = vVec[i] > 30 ? 1 : 0;
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
            iVec[i] = iVec[i] + sumVec[i];
            vVec[i] = vVec[i]+0.04*pow(vVec[i], 2)+5*vVec[i]+140-uVec[i]+iVec[i];
            uVec[i] = uVec[i]+aVec[i]*(bVec[i]*vVec[i]-uVec[i]);
        }
        /* // Debug block
        printf("Step %d\n", step);
        printf("deltaV[sampleNeuron]: %f\n", +0.04*pow(vVec[sampleNeuron], 2));
        printf("deltaV[sampleNeuron]: %f\n", +0.04*pow(vVec[sampleNeuron], 2)+5*vVec[sampleNeuron]);
        printf("deltaV[sampleNeuron]: %f\n", +0.04*pow(vVec[sampleNeuron], 2)+5*vVec[sampleNeuron]+140);
        printf("deltaV[sampleNeuron]: %f\n", +0.04*pow(vVec[sampleNeuron], 2)+5*vVec[sampleNeuron]+140-uVec[sampleNeuron]);
        printf("deltaV[sampleNeuron]: %f\n", +0.04*pow(vVec[sampleNeuron], 2)+5*vVec[sampleNeuron]+140-uVec[sampleNeuron]+iVec[sampleNeuron]);
        printf("Stats[sampleNeuron]: I = %f, A = %f, B = %f, C = %f, D = %f, V = %f, U = %f\n", iVec[sampleNeuron], aVec[sampleNeuron], bVec[sampleNeuron], cVec[sampleNeuron], dVec[sampleNeuron], vVec[sampleNeuron], uVec[sampleNeuron]);*/
    }
    bmpPrintMat(firings, Ne+Ni, timesteps, "primo.bmp");
    //symPrintMat(firings, Ne+Ni, timesteps);
    //doublePrintMat(sampleVTracer, timesteps, 1);
}