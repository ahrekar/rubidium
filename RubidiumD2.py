#!/usr/bin/env python
# encoding: utf-8
"""
RubidiumD2.py

Software suite for calculating Rubidium D2 absorption spectra.
Based on the paper by 
Siddons et al. J. Phys. B: At. Mol. Opt. Phys. 41, 155004 (2008).

Also, heavily inspired by Mathematica code by the same author:
http://massey.dur.ac.uk/resources/resources.html
http://massey.dur.ac.uk/resources/psiddons/absdisD2.nb

Created by Andrew M. C. Dawes on 2010-07-14.
Copyright (c) 2010 Pacific University. Some rights reserved.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>."""

import sys
import os
from scipy.constants import hbar, e, epsilon_0, c, m_u, k, m_e, alpha
from scipy import sqrt, pi, exp, zeros, array, real, imag
from scipy.special import erf
from pylab import plot, show, linspace, title, xlabel, ylabel
from numpy import savetxt

a_0 = hbar/(m_e*c*alpha) # bohr radius

def u87(T):
    """Mean thermal velocity for 87-Rb"""
    return sqrt(2*k*T/(86.909180520*m_u))

def u85(T):
    """Mean thermal velocity for 85-Rb"""
    return sqrt(2*k*T/(84.911789732*m_u))
    
    
def P(T):
    """Vapor pressure in a thermal cell"""
    # return 7e-8 # <--- USE THIS for finding background P
    if (T<312.46):
        return 10**(2.88081+4.857-4215.0/T)
    else:
        return 10**(2.88081+4.312-4040.0/T)

        
abundance = {"85":0.7217,"87":0.2783}

def N(T,isotope):
    """Atomic number density at T for given isotope"""
    return abundance[isotope]*P(T)*133.323/(k*T)
    
lProbe = 780.241e-9

kProbe = 2*pi/lProbe

omegaProbe = kProbe/c

Gamma2 = 2*pi*6.065e6 # Excited state decay rate

d21 = sqrt(3)*sqrt(3*epsilon_0*hbar*Gamma2*lProbe**3/(8*pi**2)) # reduced matrix element

#####################################
# ELECTRICAL SUSCEPTIBILITY CONSTANTS
#####################################

def dispersion(a,y):
    return 1j/2.0*sqrt(pi)*(exp(1/4.0*(a-2j*y)**2)*(1-erf(a/2-1j*y))-exp(1/4.0*(a+2*1j*y)**2)*(1-erf(a/2.0+1j*y)))

def voigt(a,y):
    return sqrt(pi)/2.0*(exp(1/4.0*(a-2j*y)**2)*((1-erf(a/2.0-1j*y))+exp(2*1j*a*y)*(1-erf(a/2.0+1j*y))))

def lo87(T):
    return Gamma2/(kProbe*u87(T))
    
def D87(y, T):
    return dispersion(lo87(T),y)
    
def V87(y, T):
    return voigt(lo87(T),y)

def lo85(T):
    return Gamma2/(kProbe*u85(T))

def D85(y, T):
    return dispersion(lo85(T),y)

def V85(y, T):
    return voigt(lo85(T),y)

# Transition strength factors C_F^2, call as F87[1][2] for the F=1 to F'=2 strength

F87 = [[ 0.0, 0.0, 0.0, 0.0],
       [ 1/9.0, 5/18.0, 5/18.0, 0.0],
       [ 0.0,  1/18.0, 5/18.0, 7/9.0]]
       
F85 = [[ 0.0, 0.0, 0.0, 0.0, 0.0],
       [ 0.0, 0.0, 0.0, 0.0, 0.0],
       [ 0.0, 1/3.0, 35/81.0, 28/81.0, 0.0],
       [ 0.0, 0.0,  10/81.0, 35/81.0, 1.0]]
       
# Detuning factors, call as det87[1][2] for the F=1 to F'=2 hyperfine transition

detF87 = [[ 0.0, 0.0, 0.0, 0.0],
          [ -4027.403e6, -4099.625e6, -4256.570e6, 0.0],
          [ 0.0,  2735.050e6, 2578.110e6, 2311.260e6]]
       
detF85 = [[ 0.0, 0.0, 0.0, 0.0, 0.0],
          [ 0.0, 0.0, 0.0, 0.0, 0.0],
          [ 0.0, -1635.454e6, -1664.714e6, -1728.134e6, 0.0],
          [ 0.0, 0.0, 1371.290e6, 1307.870e6, 1186.910e6]]
       
def K87(T,Fg,Fe):
    return F87[Fg][Fe]*1/8.0*1/(hbar*epsilon_0) * d21**2 * N(T,"87")/(kProbe * u87(T))

def K85(T,Fg,Fe):
    return F85[Fg][Fe]*1/12.0*1/(hbar*epsilon_0) * d21**2 * N(T,"85")/(kProbe * u85(T))

def chiRe87(delta,T,Fg,Fe):
    """The real part of the susceptibility for 87-Rb"""
    return K87(T,Fg,Fe)*real(D87(2*pi*(delta+detF87[Fg][Fe])/(kProbe*u87(T)),T))

def chiIm87(delta,T,Fg,Fe):
    """The imaginary part of the susceptibility for 87-Rb"""
    return K87(T,Fg,Fe)*real(V87(2*pi*(delta+detF87[Fg][Fe])/(kProbe*u87(T)),T))
        
def chiRe85(delta,T,Fg,Fe):
    """The real part of the susceptibility for 85-Rb"""
    return K85(T,Fg,Fe)*real(D85(2*pi*(delta+detF85[Fg][Fe])/(kProbe*u85(T)),T))

def chiIm85(delta,T,Fg,Fe):
    """The imaginary part of the susceptibility for 85-Rb"""
    return K85(T,Fg,Fe)*real(V85(2*pi*(delta+detF85[Fg][Fe])/(kProbe*u85(T)),T))

def TotalChiRe(delta,T):
    """The total real part of the susceptibility is the sum of each transition"""
    return chiRe87(delta,T,1,0) + chiRe87(delta,T,1,1) + chiRe87(delta,T,1,2) + chiRe87(delta,T,2,1) + chiRe87(delta,T,2,2) + chiRe87(delta,T,2,3) + chiRe85(delta,T,2,1) + chiRe85(delta,T,2,2) + chiRe85(delta,T,2,3) + chiRe85(delta,T,3,2) + chiRe85(delta,T,3,3) + chiRe85(delta,T,3,4)
    
def TotalChiIm(delta,T):
    """The total imaginary part of the susceptibility is the sum of each transition"""
    return chiIm87(delta,T,1,0) + chiIm87(delta,T,1,1) + chiIm87(delta,T,1,2) + chiIm87(delta,T,2,1) + chiIm87(delta,T,2,2) + chiIm87(delta,T,2,3) + chiIm85(delta,T,2,1) + chiIm85(delta,T,2,2) + chiIm85(delta,T,2,3) + chiIm85(delta,T,3,2) + chiIm85(delta,T,3,3) + chiIm85(delta,T,3,4)
    
def Totaln(delta,T):
    return 1+1/2.0*TotalChiRe(delta,T)
    
def TotalAlpha(delta,T):
    return kProbe*TotalChiIm(delta,T)
    
def AbsorptionProfile(delta,T,Lc):
    """Absorption profile as a function of detuning, temperature, and cell length"""
    return exp(-TotalAlpha(delta,T)*Lc)


def main():
    T = 285 # Temperature in Kelvin
    Lc = 0.075 # Length of cell in meters
    delta = linspace(-4,6,200)
    absdata = AbsorptionProfile(delta*1e9,T,Lc)
    plot(delta,absdata)
    title("Rubidium D2 Spectrum at T= " + str(T) + " K")
    xlabel(r"Detuning \Delta (GHz)")
    ylabel("Transmission (Arb. Units)")
    show()
    savetxt("D2AbsorptionData.dat",absdata)


if __name__ == '__main__':
	main()

