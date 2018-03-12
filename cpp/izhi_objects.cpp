#include<iostream>
#include<cstdlib>
#include<cmath>
#include<string>
#include<mtwist/mtwist.h>

//To save output
#include <png++/png.hpp>

//NOTE: we may need to cite Armadillo. Paper link on their site.
#include<armadillo>

#define FIRING_THRESHOLD 30.0

using namespace std;


void pngPrintMat(arma::mat toprint, int width, int height, string filename) {
    png::image< png::rgb_pixel > image(width, height);
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            int val = 255*(1-toprint(y,x));
            image[y][x] = png::rgb_pixel(val, val, val);
        }
    }
    image.write(filename);
}

double BMRandom() {
    // Box-Mueller. mtwist is enigmatic as ever.
    double U = mt_drand();
    double V = mt_drand();
    return sqrt(-2*log(U))*cos(6.283*V);
}

class izhiNeuron {
    private:
    double a, b, c, d;
    double u, v;
    bool fired;
    
    public:
    izhiNeuron(double a, double b, double c, double d);
    void update(double I);
    bool getFired(){return fired;};
};

izhiNeuron::izhiNeuron(double a, double b, double c, double d){
    this->a = a;
    this->b = b;
    this->c = c;
    this->d = d;
    
    this->v = -65.0;
    this->u = this->b*this->v;
    
    this->fired = false;
}

void izhiNeuron::update(double I){
    if(v>FIRING_THRESHOLD){
        fired = true;
        v = c;
        u += d;
    } else {
        fired = false; //In case it fired at the previous step
    }
    v += 0.04*pow(v,2)+5*v+140-u+I;
    u += a*(b*v-u);
}

izhiNeuron** paperStructure(int Ne, int Ni) {
    izhiNeuron** out = (izhiNeuron**)malloc((Ne+Ni)*sizeof(izhiNeuron*));
    for(int i = 0; i < Ne; i++) {
        double re = mt_drand();
        izhiNeuron* tmpn = new izhiNeuron(0.02, 0.2, -65+15*pow(re, 2), 8-6*pow(re,2));
        out[i] = tmpn;
    }
    for (int i = Ne; i < Ne+Ni; i++) {
        double ri = mt_drand();
        izhiNeuron* tmpn = new izhiNeuron(0.02+0.08*ri, 0.25-0.05*ri, -65, 2);
        out[i] = tmpn;
    }
    return out;
}

arma::mat randomConnMat(int Ne, int Ni) {
    arma::mat S = arma::mat(Ne+Ni, Ne+Ni);
    for(int i = 0; i < Ne+Ni; i++) {
        for(int j = 0; j < Ne; j++) {
            S(j,i) = 0.5*mt_drand();
        }
        for(int j = Ne; j < Ne+Ni; j++) {
            S(j,i) = -1*mt_drand();
        }
    }
    return S;
}

int main(int argc, char* argv[]) {
    mt_seed();
    
    cout << "Beginning execution" << endl;
    
    //NOTE: Here we could add a parser, so that the net cconfiguration can be specified by a JSON, CSV or other parsable file format
    
    //double tmp = mt_drand();
    int timelimit = 1000;
    int Ne = 800;
    int Ni = 200;
    izhiNeuron** sample = paperStructure(Ne, Ni);
    arma::mat S = randomConnMat(Ne, Ni);
    
    // I guess it's costly to re-initialize them every time.
    arma::rowvec I = arma::rowvec(Ne+Ni);
    arma::rowvec fired = arma::rowvec(Ne+Ni);
    arma::rowvec tmp = arma::rowvec(Ne+Ni);
    
    arma::mat firings = arma::mat(Ne+Ni, timelimit);
    
    for(int step = 0; step < timelimit; step++) {
        if(step%100 == 0)
            cout << "Step " << step+1 << endl;
        for(int i = 0; i < Ne+Ni; i++) {
            I(i) = (i < Ne ? 5 : 2)*BMRandom();
            fired(i) = sample[i]->getFired() ? 1 : 0;
            firings(step, i) = fired[i];
        }
        tmp = fired*S;
        I += tmp;
        for(int i = 0; i < Ne+Ni; i++) {
            sample[i]->update(I[i]);
        }
    }
    cout << "Saving..." << endl;
    pngPrintMat(firings, Ne+Ni, timelimit, "cpp.png");
}