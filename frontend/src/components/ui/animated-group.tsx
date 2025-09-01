/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";
import React, { ReactNode } from "react";
import { motion, Variants } from "motion/react";
import { JSX } from "react/jsx-runtime";

export type PresetType =
	| "fade"
	| "slide"
	| "scale"
	| "blur"
	| "blur-slide"
	| "zoom"
	| "flip"
	| "bounce"
	| "rotate"
	| "swing";

type As = keyof JSX.IntrinsicElements | React.ComponentType<any>;

export type AnimatedGroupProps = {
	children: ReactNode;
	className?: string;
	variants?: {
		container?: Variants;
		item?: Variants;
	};
	preset?: PresetType;
	as?: As;
	asChild?: As;
};

const defaultContainerVariants: Variants = {
	visible: {
		transition: { staggerChildren: 0.1 },
	},
};

const defaultItemVariants: Variants = {
	hidden: { opacity: 0 },
	visible: { opacity: 1 },
};

const presetVariants: Record<PresetType, Variants> = {
	fade: {},
	slide: { hidden: { y: 20 }, visible: { y: 0 } },
	scale: { hidden: { scale: 0.8 }, visible: { scale: 1 } },
	blur: { hidden: { filter: "blur(4px)" }, visible: { filter: "blur(0px)" } },
	"blur-slide": {
		hidden: { filter: "blur(4px)", y: 20 },
		visible: { filter: "blur(0px)", y: 0 },
	},
	zoom: {
		hidden: { scale: 0.5 },
		visible: { scale: 1, transition: { type: "spring", stiffness: 300, damping: 20 } },
	},
	flip: {
		hidden: { rotateX: -90 },
		visible: { rotateX: 0, transition: { type: "spring", stiffness: 300, damping: 20 } },
	},
	bounce: {
		hidden: { y: -50 },
		visible: { y: 0, transition: { type: "spring", stiffness: 400, damping: 10 } },
	},
	rotate: {
		hidden: { rotate: -180 },
		visible: { rotate: 0, transition: { type: "spring", stiffness: 200, damping: 15 } },
	},
	swing: {
		hidden: { rotate: -10 },
		visible: { rotate: 0, transition: { type: "spring", stiffness: 300, damping: 8 } },
	},
};

const addDefaultVariants = (variants?: Variants): Variants => ({
	hidden: { ...(defaultItemVariants.hidden || {}), ...((variants?.hidden as object) || {}) },
	visible: { ...(defaultItemVariants.visible || {}), ...((variants?.visible as object) || {}) },
});

// Prefer built-in motion tags (motion.div, motion.section, etc.)
// and fall back to motion.create for custom components.
function getMotionComponent(as: As) {
	const maybeIntrinsic = (motion as any)[as as any];
	if (maybeIntrinsic) return maybeIntrinsic as React.ComponentType<any>;
	return (motion as any).create(as as string | React.ComponentType<any>) as React.ComponentType<any>;
}

function AnimatedGroup({ children, className, variants, preset, as = "div", asChild = "div" }: AnimatedGroupProps) {
	const selectedVariants = {
		item: addDefaultVariants(preset ? presetVariants[preset] : {}),
		container: addDefaultVariants(defaultContainerVariants),
	};

	const containerVariants = variants?.container || selectedVariants.container;
	const itemVariants = variants?.item || selectedVariants.item;

	const MotionComponent = React.useMemo(() => getMotionComponent(as), [as]);
	const MotionChild = React.useMemo(() => getMotionComponent(asChild), [asChild]);

	return (
		<MotionComponent initial="hidden" animate="visible" variants={containerVariants} className={className}>
			{React.Children.map(children, (child, index) => (
				<MotionChild key={index} variants={itemVariants}>
					{child}
				</MotionChild>
			))}
		</MotionComponent>
	);
}

export { AnimatedGroup };
