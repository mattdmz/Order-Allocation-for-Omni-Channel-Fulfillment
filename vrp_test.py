from __future__ import print_function
from __future__ import division
from numpy import array

from vrp.paersenssavings import paessens_savings_init
from util import sol2routes

d = [7, 	9, 	16, 	6, 	15, 	0, 	0, 	6, 	4, 	10, 	4, 	16, 	3, 	8, 	18, 	4, 	5, 	12, 	5, 	10, 	12, 	3, 	13, 	4, 	5, 	4, 	16, 	7, 	12, 	15, 	8, 	20, 	7, 	10, 	18, 	16, 	7, 	20, 	2, 	13, 	17, 	5, 	13, 	3, 	20, 	4, 	7, 	10, 	9, 	18]

C=20*5

L=100*5

D = array(
    [[12, 	80, 	3, 	99, 	86, 	96, 	31, 	89, 	25, 	73, 	90, 	86, 	44, 	84, 	32, 	29, 	99, 	39, 	90, 	17, 	43, 	87, 	76, 	27, 	92, 	44, 	75, 	36, 	37, 	1, 	49, 	36, 	76, 	68, 	19, 	81, 	30, 	51, 	41, 	24, 	56, 	33, 	75, 	15, 	98, 	11, 	26, 	74, 	89, 	71],
    [44, 	71, 	90, 	52, 	73, 	90, 	14, 	0, 	56, 	54, 	57, 	6, 	21, 	36, 	83, 	20, 	83, 	46, 	40, 	3, 	51, 	66, 	71, 	62, 	96, 	31, 	22, 	94, 	97, 	55, 	84, 	81, 	100, 	72, 	62, 	97, 	60, 	33, 	71, 	76, 	40, 	56, 	97, 	42, 	54, 	57, 	98, 	46, 	20, 	6],
    [50, 	68, 	89, 	42, 	25, 	1, 	53, 	46, 	40, 	66, 	91, 	62, 	82, 	77, 	60, 	49, 	13, 	45, 	81, 	83, 	14, 	78, 	96, 	59, 	22, 	87, 	44, 	11, 	84, 	49, 	11, 	35, 	49, 	27, 	11, 	63, 	78, 	70, 	63, 	39, 	51, 	74, 	70, 	7, 	5, 	3, 	100, 	21, 	2, 	76],
    [75, 	16, 	47, 	43, 	46, 	46, 	3, 	24, 	1, 	11, 	42, 	61, 	47, 	31, 	74, 	98, 	21, 	14, 	30, 	27, 	17, 	5, 	41, 	19, 	38, 	30, 	43, 	61, 	31, 	58, 	26, 	8, 	44, 	17, 	41, 	50, 	39, 	43, 	85, 	84, 	60, 	73, 	42, 	75, 	10, 	80, 	10, 	78, 	2, 	33],
    [16, 	0, 	71, 	65, 	84, 	82, 	18, 	89, 	76, 	30, 	69, 	3, 	63, 	2, 	5, 	3, 	39, 	16, 	15, 	60, 	89, 	31, 	87, 	79, 	97, 	71, 	47, 	1, 	96, 	18, 	69, 	28, 	23, 	43, 	89, 	80, 	18, 	33, 	73, 	93, 	70, 	3, 	43, 	31, 	31, 	78, 	27, 	58, 	9, 	9],
    [96, 	75, 	59, 	75, 	58, 	94, 	26, 	83, 	74, 	73, 	52, 	39, 	12, 	91, 	58, 	35, 	37, 	69, 	58, 	50, 	7, 	12, 	35, 	78, 	82, 	24, 	15, 	22, 	45, 	43, 	24, 	33, 	0, 	25, 	10, 	52, 	1, 	27, 	47, 	89, 	84, 	40, 	22, 	50, 	68, 	37, 	6, 	10, 	82, 	93],
    [85, 	35, 	1, 	72, 	6, 	13, 	66, 	93, 	64, 	21, 	19, 	86, 	91, 	3, 	81, 	25, 	51, 	56, 	14, 	96, 	56, 	93, 	18, 	63, 	78, 	19, 	25, 	55, 	44, 	30, 	62, 	44, 	80, 	24, 	26, 	47, 	87, 	12, 	70, 	61, 	98, 	69, 	49, 	35, 	58, 	6, 	87, 	23, 	86, 	38],
    [18, 	57, 	40, 	18, 	30, 	77, 	74, 	81, 	93, 	27, 	17, 	0, 	38, 	100, 	38, 	16, 	98, 	83, 	60, 	58, 	79, 	68, 	18, 	20, 	37, 	100, 	1, 	20, 	57, 	44, 	8, 	72, 	32, 	2, 	89, 	7, 	51, 	48, 	57, 	18, 	34, 	43, 	51, 	65, 	42, 	61, 	13, 	47, 	6, 	48],
    [42, 	99, 	97, 	44, 	60, 	18, 	21, 	39, 	30, 	19, 	66, 	93, 	31, 	2, 	34, 	58, 	42, 	3, 	55, 	36, 	59, 	8, 	5, 	18, 	83, 	14, 	4, 	45, 	88, 	77, 	24, 	98, 	50, 	51, 	100, 	93, 	16, 	26, 	70, 	36, 	86, 	59, 	37, 	19, 	41, 	85, 	4, 	57, 	40, 	99],
    [57, 	20, 	23, 	9, 	71, 	69, 	73, 	82, 	86, 	98, 	100, 	34, 	20, 	63, 	72, 	12, 	56, 	45, 	80, 	43, 	46, 	62, 	9, 	68, 	3, 	84, 	9, 	49, 	86, 	79, 	8, 	40, 	83, 	82, 	63, 	28, 	43, 	42, 	47, 	24, 	80, 	38, 	25, 	5, 	23, 	3, 	16, 	49, 	94, 	57],
    [29, 	53, 	12, 	76, 	58, 	77, 	21, 	69, 	25, 	64, 	13, 	95, 	44, 	83, 	25, 	47, 	89, 	72, 	71, 	36, 	46, 	37, 	39, 	45, 	4, 	58, 	29, 	29, 	11, 	49, 	31, 	21, 	44, 	66, 	92, 	31, 	12, 	59, 	35, 	23, 	26, 	88, 	70, 	96, 	19, 	34, 	55, 	52, 	60, 	24],
    [94, 	36, 	79, 	37, 	20, 	29, 	54, 	26, 	4, 	79, 	4, 	15, 	7, 	73, 	36, 	50, 	50, 	56, 	81, 	17, 	90, 	63, 	5, 	33, 	30, 	19, 	1, 	21, 	66, 	34, 	60, 	35, 	70, 	91, 	85, 	79, 	0, 	18, 	5, 	1, 	48, 	76, 	99, 	0, 	21, 	15, 	43, 	50, 	81, 	16],
    [59, 	25, 	30, 	16, 	22, 	1, 	62, 	52, 	64, 	98, 	26, 	69, 	24, 	77, 	63, 	21, 	8, 	27, 	21, 	17, 	7, 	83, 	35, 	6, 	24, 	79, 	28, 	44, 	66, 	8, 	97, 	24, 	83, 	49, 	82, 	72, 	12, 	6, 	0, 	68, 	54, 	6, 	31, 	89, 	49, 	27, 	87, 	97, 	80, 	29],
    [46, 	85, 	80, 	7, 	76, 	83, 	94, 	40, 	17, 	49, 	23, 	69, 	18, 	82, 	67, 	9, 	60, 	30, 	58, 	97, 	70, 	33, 	52, 	98, 	99, 	72, 	88, 	54, 	61, 	54, 	1, 	16, 	89, 	6, 	50, 	33, 	44, 	19, 	82, 	100, 	35, 	89, 	8, 	67, 	6, 	31, 	96, 	42, 	16, 	31],
    [75, 	43, 	100, 	83, 	50, 	21, 	92, 	47, 	94, 	100, 	13, 	30, 	40, 	26, 	5, 	76, 	89, 	44, 	68, 	87, 	63, 	26, 	43, 	22, 	44, 	80, 	45, 	30, 	91, 	26, 	81, 	18, 	81, 	78, 	81, 	20, 	21, 	90, 	33, 	4, 	45, 	6, 	82, 	25, 	93, 	66, 	50, 	72, 	21, 	90],
    [65, 	80, 	50, 	61, 	29, 	89, 	38, 	99, 	92, 	60, 	65, 	18, 	18, 	70, 	25, 	20, 	100, 	1, 	33, 	61, 	10, 	71, 	10, 	89, 	63, 	43, 	88, 	32, 	23, 	40, 	31, 	35, 	50, 	22, 	84, 	48, 	64, 	1, 	65, 	50, 	42, 	10, 	58, 	76, 	57, 	69, 	80, 	54, 	87, 	13],
    [66, 	26, 	56, 	8, 	16, 	1, 	64, 	89, 	33, 	4, 	97, 	0, 	21, 	98, 	92, 	1, 	59, 	64, 	52, 	62, 	18, 	99, 	59, 	49, 	29, 	2, 	14, 	79, 	55, 	53, 	75, 	2, 	19, 	13, 	52, 	55, 	69, 	31, 	45, 	55, 	55, 	25, 	54, 	69, 	100, 	22, 	43, 	98, 	7, 	38],
    [22, 	8, 	42, 	14, 	63, 	20, 	99, 	84, 	74, 	31, 	22, 	70, 	5, 	4, 	74, 	29, 	12, 	36, 	1, 	84, 	5, 	7, 	7, 	46, 	53, 	41, 	23, 	61, 	67, 	73, 	99, 	70, 	43, 	57, 	47, 	52, 	97, 	89, 	45, 	48, 	32, 	68, 	17, 	86, 	45, 	17, 	14, 	37, 	66, 	9],
    [92, 	58, 	12, 	74, 	63, 	7, 	14, 	83, 	7, 	40, 	50, 	17, 	83, 	65, 	7, 	30, 	36, 	4, 	35, 	33, 	74, 	81, 	78, 	1, 	10, 	28, 	57, 	24, 	56, 	8, 	76, 	23, 	17, 	59, 	16, 	80, 	0, 	8, 	53, 	94, 	44, 	64, 	68, 	85, 	44, 	88, 	81, 	8, 	70, 	45],
    [52, 	42, 	46, 	41, 	7, 	80, 	25, 	71, 	38, 	61, 	79, 	33, 	63, 	53, 	38, 	59, 	62, 	14, 	94, 	58, 	45, 	25, 	11, 	23, 	17, 	47, 	56, 	26, 	30, 	6, 	83, 	39, 	100, 	47, 	78, 	62, 	86, 	28, 	78, 	47, 	46, 	5, 	62, 	86, 	2, 	68, 	94, 	49, 	32, 	91],
    [28, 	76, 	58, 	64, 	78, 	32, 	78, 	53, 	6, 	83, 	15, 	3, 	53, 	53, 	76, 	66, 	97, 	65, 	68, 	86, 	68, 	28, 	22, 	6, 	73, 	66, 	0, 	3, 	97, 	74, 	15, 	52, 	42, 	21, 	83, 	61, 	14, 	74, 	83, 	64, 	19, 	92, 	6, 	81, 	60, 	99, 	48, 	75, 	3, 	31],
    [23, 	92, 	35, 	31, 	78, 	82, 	94, 	19, 	65, 	74, 	67, 	22, 	39, 	72, 	6, 	96, 	51, 	83, 	36, 	40, 	46, 	19, 	89, 	99, 	60, 	20, 	25, 	99, 	57, 	67, 	20, 	30, 	63, 	91, 	70, 	12, 	46, 	94, 	73, 	59, 	97, 	90, 	4, 	90, 	10, 	5, 	7, 	94, 	84, 	79],
    [94, 	53, 	89, 	29, 	92, 	28, 	70, 	98, 	26, 	94, 	0, 	28, 	52, 	2, 	95, 	79, 	32, 	65, 	37, 	39, 	99, 	50, 	89, 	52, 	74, 	85, 	1, 	87, 	9, 	96, 	12, 	84, 	57, 	21, 	13, 	15, 	22, 	70, 	20, 	58, 	69, 	29, 	18, 	47, 	25, 	27, 	12, 	21, 	76, 	13],
    [99, 	33, 	36, 	12, 	90, 	44, 	71, 	100, 	41, 	34, 	82, 	47, 	6, 	67, 	63, 	7, 	53, 	97, 	37, 	19, 	72, 	66, 	56, 	60, 	91, 	40, 	84, 	25, 	56, 	9, 	91, 	60, 	37, 	33, 	62, 	68, 	46, 	1, 	65, 	73, 	0, 	2, 	86, 	82, 	13, 	71, 	92, 	7, 	6, 	9],
    [46, 	48, 	95, 	69, 	4, 	35, 	75, 	0, 	41, 	38, 	81, 	43, 	40, 	52, 	50, 	66, 	37, 	6, 	60, 	83, 	76, 	39, 	41, 	42, 	63, 	39, 	88, 	93, 	15, 	72, 	80, 	20, 	9, 	56, 	71, 	24, 	46, 	73, 	51, 	56, 	19, 	75, 	39, 	80, 	14, 	12, 	5, 	1, 	83, 	45],
    [2, 	19, 	17, 	62, 	80, 	30, 	80, 	1, 	69, 	52, 	74, 	78, 	97, 	34, 	36, 	82, 	3, 	16, 	54, 	43, 	17, 	34, 	60, 	62, 	28, 	66, 	7, 	41, 	36, 	42, 	22, 	100, 	85, 	47, 	86, 	52, 	50, 	38, 	30, 	27, 	70, 	64, 	18, 	83, 	15, 	89, 	86, 	20, 	93, 	42],
    [44, 	22, 	1, 	94, 	45, 	56, 	81, 	12, 	10, 	38, 	25, 	5, 	24, 	30, 	95, 	27, 	36, 	81, 	98, 	41, 	13, 	24, 	89, 	34, 	91, 	89, 	76, 	2, 	68, 	96, 	93, 	23, 	82, 	81, 	37, 	45, 	6, 	64, 	84, 	53, 	66, 	40, 	38, 	54, 	39, 	57, 	14, 	82, 	49, 	94],
    [7, 	70, 	9, 	63, 	54, 	49, 	56, 	23, 	15, 	54, 	57, 	25, 	80, 	34, 	30, 	9, 	7, 	49, 	7, 	19, 	91, 	29, 	63, 	53, 	54, 	47, 	28, 	26, 	38, 	72, 	31, 	90, 	91, 	82, 	89, 	46, 	10, 	10, 	68, 	12, 	55, 	50, 	64, 	77, 	70, 	35, 	56, 	20, 	84, 	93],
    [14, 	51, 	82, 	14, 	92, 	98, 	88, 	78, 	86, 	26, 	12, 	69, 	16, 	29, 	76, 	52, 	6, 	45, 	46, 	54, 	27, 	71, 	40, 	66, 	67, 	89, 	27, 	83, 	86, 	38, 	83, 	15, 	79, 	5, 	60, 	75, 	100, 	28, 	55, 	5, 	86, 	91, 	74, 	50, 	7, 	95, 	25, 	66, 	77, 	17],
    [25, 	51, 	74, 	22, 	95, 	47, 	68, 	51, 	20, 	5, 	17, 	42, 	20, 	26, 	20, 	100, 	57, 	49, 	75, 	6, 	79, 	64, 	37, 	39, 	80, 	2, 	18, 	42, 	98, 	60, 	3, 	75, 	59, 	50, 	89, 	95, 	49, 	63, 	18, 	43, 	77, 	32, 	35, 	52, 	46, 	20, 	56, 	95, 	35, 	29],
    [73, 	10, 	88, 	91, 	62, 	42, 	9, 	55, 	63, 	55, 	28, 	99, 	10, 	36, 	65, 	46, 	39, 	11, 	70, 	47, 	63, 	52, 	54, 	50, 	66, 	7, 	48, 	92, 	7, 	0, 	50, 	96, 	99, 	5, 	15, 	18, 	0, 	91, 	55, 	76, 	30, 	76, 	48, 	83, 	40, 	65, 	100, 	89, 	45, 	0],
    [100, 	75, 	16, 	12, 	3, 	18, 	63, 	27, 	42, 	46, 	95, 	63, 	9, 	0, 	50, 	58, 	45, 	91, 	39, 	100, 	7, 	63, 	84, 	0, 	80, 	59, 	66, 	70, 	57, 	72, 	89, 	88, 	10, 	93, 	41, 	39, 	25, 	59, 	55, 	100, 	23, 	32, 	82, 	0, 	86, 	1, 	35, 	25, 	28, 	50],
    [72, 	24, 	12, 	42, 	11, 	36, 	11, 	41, 	16, 	83, 	17, 	73, 	68, 	46, 	73, 	86, 	6, 	6, 	14, 	25, 	58, 	7, 	77, 	92, 	58, 	79, 	15, 	18, 	33, 	84, 	9, 	22, 	14, 	53, 	12, 	71, 	100, 	55, 	39, 	54, 	49, 	100, 	92, 	35, 	7, 	98, 	10, 	41, 	45, 	32],
    [76, 	51, 	65, 	30, 	94, 	13, 	100, 	68, 	72, 	34, 	32, 	67, 	73, 	94, 	72, 	47, 	40, 	57, 	88, 	17, 	15, 	25, 	33, 	9, 	76, 	41, 	39, 	26, 	32, 	89, 	13, 	32, 	36, 	65, 	45, 	96, 	2, 	6, 	52, 	62, 	18, 	64, 	94, 	91, 	9, 	67, 	15, 	36, 	18, 	95],
    [35, 	82, 	48, 	21, 	85, 	53, 	10, 	14, 	39, 	58, 	2, 	24, 	67, 	50, 	68, 	74, 	24, 	52, 	90, 	6, 	19, 	42, 	67, 	6, 	48, 	48, 	26, 	68, 	84, 	29, 	26, 	40, 	87, 	62, 	7, 	90, 	41, 	74, 	45, 	88, 	38, 	23, 	61, 	21, 	99, 	12, 	69, 	52, 	34, 	16],
    [74, 	54, 	58, 	88, 	85, 	87, 	33, 	84, 	23, 	46, 	68, 	23, 	82, 	51, 	36, 	17, 	77, 	19, 	4, 	3, 	10, 	10, 	32, 	23, 	5, 	56, 	85, 	45, 	93, 	13, 	3, 	2, 	34, 	35, 	20, 	49, 	58, 	93, 	58, 	2, 	92, 	12, 	83, 	3, 	9, 	40, 	86, 	28, 	5, 	100],
    [39, 	65, 	30, 	58, 	16, 	30, 	63, 	15, 	3, 	31, 	93, 	70, 	40, 	59, 	48, 	91, 	38, 	89, 	16, 	73, 	15, 	7, 	41, 	73, 	39, 	84, 	65, 	97, 	97, 	14, 	68, 	10, 	14, 	41, 	7, 	21, 	51, 	54, 	48, 	25, 	59, 	67, 	33, 	94, 	77, 	96, 	96, 	99, 	93, 	41],
    [77, 	26, 	10, 	24, 	55, 	19, 	3, 	83, 	98, 	32, 	77, 	10, 	22, 	47, 	82, 	21, 	53, 	59, 	43, 	30, 	64, 	24, 	90, 	36, 	81, 	52, 	23, 	83, 	70, 	36, 	71, 	30, 	75, 	3, 	93, 	100, 	81, 	28, 	6, 	49, 	10, 	2, 	26, 	65, 	71, 	7, 	83, 	56, 	49, 	44],
    [25, 	26, 	0, 	33, 	12, 	53, 	2, 	95, 	39, 	67, 	77, 	58, 	37, 	29, 	26, 	14, 	84, 	1, 	58, 	31, 	47, 	3, 	56, 	8, 	88, 	47, 	56, 	95, 	64, 	32, 	49, 	35, 	28, 	31, 	60, 	5, 	27, 	21, 	37, 	90, 	17, 	29, 	36, 	87, 	25, 	75, 	28, 	3, 	3, 	97],
    [28, 	2, 	77, 	65, 	97, 	36, 	99, 	89, 	12, 	2, 	5, 	80, 	64, 	50, 	34, 	51, 	2, 	58, 	99, 	99, 	49, 	72, 	93, 	84, 	2, 	62, 	73, 	30, 	91, 	92, 	3, 	2, 	16, 	6, 	30, 	38, 	45, 	37, 	28, 	53, 	21, 	24, 	58, 	2, 	58, 	90, 	84, 	38, 	77, 	1],
    [89, 	12, 	79, 	88, 	83, 	8, 	77, 	67, 	55, 	28, 	3, 	62, 	11, 	46, 	27, 	70, 	49, 	87, 	14, 	97, 	45, 	32, 	63, 	57, 	21, 	53, 	19, 	15, 	58, 	15, 	41, 	48, 	43, 	6, 	93, 	82, 	40, 	46, 	35, 	95, 	25, 	7, 	24, 	29, 	95, 	32, 	31, 	35, 	3, 	84],
    [43, 	23, 	77, 	28, 	2, 	21, 	14, 	84, 	19, 	47, 	45, 	78, 	82, 	63, 	70, 	36, 	6, 	24, 	100, 	76, 	64, 	64, 	77, 	49, 	8, 	63, 	80, 	23, 	81, 	31, 	16, 	5, 	53, 	95, 	46, 	6, 	38, 	26, 	11, 	6, 	48, 	45, 	31, 	43, 	47, 	16, 	25, 	17, 	24, 	26],
    [66, 	33, 	79, 	100, 	87, 	90, 	5, 	18, 	49, 	26, 	69, 	13, 	86, 	7, 	26, 	79, 	70, 	25, 	57, 	34, 	28, 	98, 	20, 	62, 	91, 	9, 	61, 	81, 	74, 	21, 	35, 	37, 	33, 	40, 	81, 	16, 	99, 	96, 	46, 	80, 	100, 	32, 	89, 	35, 	100, 	37, 	41, 	33, 	37, 	80],
    [92, 	49, 	13, 	40, 	65, 	76, 	60, 	20, 	98, 	53, 	45, 	85, 	47, 	65, 	100, 	63, 	71, 	87, 	49, 	80, 	14, 	52, 	57, 	94, 	92, 	79, 	38, 	47, 	66, 	45, 	61, 	59, 	98, 	34, 	78, 	88, 	52, 	50, 	45, 	17, 	70, 	24, 	71, 	14, 	17, 	33, 	61, 	0, 	88, 	57],
    [73, 	46, 	19, 	59, 	57, 	73, 	18, 	47, 	53, 	90, 	94, 	22, 	26, 	26, 	47, 	29, 	62, 	66, 	77, 	38, 	8, 	29, 	87, 	28, 	39, 	49, 	57, 	14, 	62, 	44, 	13, 	97, 	99, 	65, 	45, 	33, 	91, 	56, 	62, 	28, 	24, 	17, 	60, 	88, 	35, 	26, 	82, 	5, 	16, 	65],
    [73, 	67, 	98, 	67, 	22, 	92, 	95, 	13, 	28, 	50, 	99, 	55, 	56, 	32, 	46, 	55, 	42, 	73, 	25, 	58, 	7, 	20, 	2, 	49, 	88, 	48, 	0, 	52, 	49, 	26, 	22, 	72, 	74, 	9, 	48, 	11, 	59, 	13, 	29, 	1, 	40, 	22, 	64, 	60, 	31, 	33, 	30, 	74, 	3, 	87],
    [8, 	26, 	5, 	94, 	19, 	49, 	11, 	32, 	50, 	97, 	36, 	82, 	48, 	1, 	21, 	17, 	5, 	94, 	62, 	42, 	24, 	63, 	63, 	66, 	99, 	0, 	69, 	66, 	96, 	13, 	90, 	63, 	42, 	70, 	24, 	14, 	64, 	19, 	52, 	47, 	74, 	5, 	7, 	34, 	76, 	14, 	96, 	69, 	93, 	65],
    [36, 	84, 	49, 	8, 	4, 	96, 	32, 	83, 	70, 	72, 	64, 	2, 	2, 	54, 	58, 	82, 	10, 	48, 	18, 	61, 	33, 	93, 	67, 	81, 	16, 	90, 	99, 	19, 	93, 	58, 	97, 	30, 	89, 	21, 	21, 	35, 	41, 	3, 	74, 	59, 	45, 	82, 	1, 	92, 	38, 	76, 	92, 	73, 	82, 	18],
    [75, 	9, 	69, 	85, 	43, 	66, 	82, 	2, 	56, 	96, 	36, 	68, 	5, 	64, 	29, 	10, 	93, 	70, 	99, 	32, 	70, 	41, 	52, 	4, 	66, 	88, 	82, 	53, 	43, 	25, 	0, 	60, 	45, 	69, 	88, 	17, 	51, 	77, 	77, 	59, 	23, 	58, 	0, 	35, 	1, 	59, 	2, 	71, 	45, 	10],
    [83, 	53, 	55, 	49, 	57, 	11, 	48, 	94, 	59, 	1, 	29, 	37, 	7, 	16, 	40, 	32, 	51, 	93, 	92, 	90, 	95, 	96, 	70, 	47, 	85, 	72, 	65, 	34, 	52, 	72, 	94, 	89, 	25, 	60, 	84, 	95, 	3, 	88, 	63, 	97, 	2, 	83, 	69, 	48, 	75, 	98, 	92, 	94, 	49, 	89]]
    )

solution, objv = paessens_savings_init(
    D=D, 
    d=d,
    L=L, 
    C=C, minimize_K=True, return_objv=True)

for route_idx, route in enumerate(sol2routes(solution)):
    print("Route #%d : %s"%(route_idx+1, route))
    

print(objv)
