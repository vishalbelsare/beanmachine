"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[4488],{3905:function(a,e,n){n.r(e),n.d(e,{MDXContext:function(){return l},MDXProvider:function(){return N},mdx:function(){return h},useMDXComponents:function(){return o},withMDXComponents:function(){return d}});var m=n(67294);function s(a,e,n){return e in a?Object.defineProperty(a,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):a[e]=n,a}function t(){return t=Object.assign||function(a){for(var e=1;e<arguments.length;e++){var n=arguments[e];for(var m in n)Object.prototype.hasOwnProperty.call(n,m)&&(a[m]=n[m])}return a},t.apply(this,arguments)}function r(a,e){var n=Object.keys(a);if(Object.getOwnPropertySymbols){var m=Object.getOwnPropertySymbols(a);e&&(m=m.filter((function(e){return Object.getOwnPropertyDescriptor(a,e).enumerable}))),n.push.apply(n,m)}return n}function p(a){for(var e=1;e<arguments.length;e++){var n=null!=arguments[e]?arguments[e]:{};e%2?r(Object(n),!0).forEach((function(e){s(a,e,n[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(a,Object.getOwnPropertyDescriptors(n)):r(Object(n)).forEach((function(e){Object.defineProperty(a,e,Object.getOwnPropertyDescriptor(n,e))}))}return a}function i(a,e){if(null==a)return{};var n,m,s=function(a,e){if(null==a)return{};var n,m,s={},t=Object.keys(a);for(m=0;m<t.length;m++)n=t[m],e.indexOf(n)>=0||(s[n]=a[n]);return s}(a,e);if(Object.getOwnPropertySymbols){var t=Object.getOwnPropertySymbols(a);for(m=0;m<t.length;m++)n=t[m],e.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(a,n)&&(s[n]=a[n])}return s}var l=m.createContext({}),d=function(a){return function(e){var n=o(e.components);return m.createElement(a,t({},e,{components:n}))}},o=function(a){var e=m.useContext(l),n=e;return a&&(n="function"==typeof a?a(e):p(p({},e),a)),n},N=function(a){var e=o(a.components);return m.createElement(l.Provider,{value:e},a.children)},c={inlineCode:"code",wrapper:function(a){var e=a.children;return m.createElement(m.Fragment,{},e)}},x=m.forwardRef((function(a,e){var n=a.components,s=a.mdxType,t=a.originalType,r=a.parentName,l=i(a,["components","mdxType","originalType","parentName"]),d=o(n),N=s,x=d["".concat(r,".").concat(N)]||d[N]||c[N]||t;return n?m.createElement(x,p(p({ref:e},l),{},{components:n})):m.createElement(x,p({ref:e},l))}));function h(a,e){var n=arguments,s=e&&e.mdxType;if("string"==typeof a||s){var t=n.length,r=new Array(t);r[0]=x;var p={};for(var i in e)hasOwnProperty.call(e,i)&&(p[i]=e[i]);p.originalType=a,p.mdxType="string"==typeof a?a:s,r[1]=p;for(var l=2;l<t;l++)r[l]=n[l];return m.createElement.apply(null,r)}return m.createElement.apply(null,n)}x.displayName="MDXCreateElement"},38897:function(a,e,n){n.r(e),n.d(e,{assets:function(){return d},contentTitle:function(){return i},default:function(){return c},frontMatter:function(){return p},metadata:function(){return l},toc:function(){return o}});var m=n(83117),s=n(80102),t=(n(67294),n(3905)),r=["components"],p={title:"Variational Inference",sidebar_label:"Variational Inference",slug:"/variational_inference"},i=void 0,l={unversionedId:"framework_topics/variational_inference",id:"framework_topics/variational_inference",title:"Variational Inference",description:"Params",source:"@site/../docs/framework_topics/variational_inference.md",sourceDirName:"framework_topics",slug:"/variational_inference",permalink:"/docs/variational_inference",draft:!1,editUrl:"https://github.com/facebookresearch/beanmachine/edit/main/website/../docs/framework_topics/variational_inference.md",tags:[],version:"current",frontMatter:{title:"Variational Inference",sidebar_label:"Variational Inference",slug:"/variational_inference"},sidebar:"someSidebar",previous:{title:"Block Inference",permalink:"/docs/block_inference"},next:{title:"Diagnostics",permalink:"/docs/diagnostics"}},d={},o=[{value:"Params",id:"params",level:2},{value:"Variational Worlds",id:"variational-worlds",level:2},{value:"Gradient Estimators and Divergences",id:"gradient-estimators-and-divergences",level:2},{value:"VariationalInfer",id:"variationalinfer",level:2},{value:"AutoGuides",id:"autoguides",level:2},{value:"ADVI",id:"advi",level:3},{value:"MAP",id:"map",level:3}],N={toc:o};function c(a){var e=a.components,n=(0,s.Z)(a,r);return(0,t.mdx)("wrapper",(0,m.Z)({},N,n,{components:e,mdxType:"MDXLayout"}),(0,t.mdx)("h2",{id:"params"},"Params"),(0,t.mdx)("p",null,"A ",(0,t.mdx)("a",{parentName:"p",href:"https://beanmachine.org/api/beanmachine.ppl.model.html?highlight=param#beanmachine.ppl.model.param"},(0,t.mdx)("inlineCode",{parentName:"a"},"Param"))," represents\na variational parameter to be optimized during variational inference.\nUse ",(0,t.mdx)("inlineCode",{parentName:"p"},"@bm.param"),' to decorate an "initialization fuction" which returns a\ntensor value to initialize the variational parameter at the start of optimization.'),(0,t.mdx)("h2",{id:"variational-worlds"},"Variational Worlds"),(0,t.mdx)("p",null,"A ",(0,t.mdx)("a",{parentName:"p",href:"https://beanmachine.org/api/beanmachine.ppl.inference.vi.variational_world.html#beanmachine.ppl.inference.vi.variational_world.VariationalWorld"},(0,t.mdx)("inlineCode",{parentName:"a"},"VariationalWorld")),"\nis a sub-class of ",(0,t.mdx)("a",{parentName:"p",href:"https://beanmachine.org/api/beanmachine.ppl.world.html#beanmachine.ppl.world.World"},(0,t.mdx)("inlineCode",{parentName:"a"},"World")),"\nwhich also contains data on guide distributions and their parameters, specifically:"),(0,t.mdx)("ul",null,(0,t.mdx)("li",{parentName:"ul"},(0,t.mdx)("inlineCode",{parentName:"li"},"get_guide_distribution"),": given a ",(0,t.mdx)("inlineCode",{parentName:"li"},"RVIdentifier"),", returns its corresponding guide distribution"),(0,t.mdx)("li",{parentName:"ul"},(0,t.mdx)("inlineCode",{parentName:"li"},"get_param"),": given a ",(0,t.mdx)("inlineCode",{parentName:"li"},"RVIdentifier")," for a ",(0,t.mdx)("inlineCode",{parentName:"li"},"Param"),", returns (possibly initializing if empty) the value of the parameter")),(0,t.mdx)("p",null,(0,t.mdx)("strong",{parentName:"p"},"Note"),": An implementation detail is that ",(0,t.mdx)("inlineCode",{parentName:"p"},"update_graph")," is overriden such that the\nguide distribution is automatically used if one is available."),(0,t.mdx)("h2",{id:"gradient-estimators-and-divergences"},"Gradient Estimators and Divergences"),(0,t.mdx)("p",null,"A ",(0,t.mdx)("a",{parentName:"p",href:"https://beanmachine.org/api/beanmachine.ppl.inference.vi.gradient_estimator.html"},(0,t.mdx)("inlineCode",{parentName:"a"},"gradient_estimator")),"\ncomputes a Monte-Carlo (possibly surrogate) objective estimate whose gradients\nare used as the training signal."),(0,t.mdx)("p",null,"We structure our VI objective following abstractions introduced in\n",(0,t.mdx)("a",{parentName:"p",href:"https://arxiv.org/abs/2009.13093"},"f-Divergence Variational Inference"),", where\n",(0,t.mdx)("inlineCode",{parentName:"p"},"gradient_estimator")," takes as input a ",(0,t.mdx)("a",{parentName:"p",href:"https://beanmachine.org/api/beanmachine.ppl.inference.vi.discrepancy.html"},"discrepancy\nfunction"),"\ncorresponding to an ",(0,t.mdx)("span",{parentName:"p",className:"math math-inline"},(0,t.mdx)("span",{parentName:"span",className:"katex"},(0,t.mdx)("span",{parentName:"span",className:"katex-mathml"},(0,t.mdx)("math",{parentName:"span",xmlns:"http://www.w3.org/1998/Math/MathML"},(0,t.mdx)("semantics",{parentName:"math"},(0,t.mdx)("mrow",{parentName:"semantics"},(0,t.mdx)("mi",{parentName:"mrow"},"f")),(0,t.mdx)("annotation",{parentName:"semantics",encoding:"application/x-tex"},"f")))),(0,t.mdx)("span",{parentName:"span",className:"katex-html","aria-hidden":"true"},(0,t.mdx)("span",{parentName:"span",className:"base"},(0,t.mdx)("span",{parentName:"span",className:"strut",style:{height:"0.8888799999999999em",verticalAlign:"-0.19444em"}}),(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal",style:{marginRight:"0.10764em"}},"f"))))),"-divergence."),(0,t.mdx)("h2",{id:"variationalinfer"},"VariationalInfer"),(0,t.mdx)("p",null,"The ",(0,t.mdx)("a",{parentName:"p",href:"https://beanmachine.org/api/beanmachine.ppl.inference.vi.variational_infer.html#beanmachine.ppl.inference.vi.variational_infer.VariationalInfer"},(0,t.mdx)("inlineCode",{parentName:"a"},"VariationalInfer")),"\nclass provides an entrypoint for VI. Model and guide ",(0,t.mdx)("inlineCode",{parentName:"p"},"RVIdentifier"),"s are associated in the\nconstructor's ",(0,t.mdx)("inlineCode",{parentName:"p"},"queries_to_guides")," argument and optimizater configuration is provided through\na ",(0,t.mdx)("inlineCode",{parentName:"p"},"optimizer")," callback. An ",(0,t.mdx)("inlineCode",{parentName:"p"},"infer()")," method is provided for easy invocation whereas ",(0,t.mdx)("inlineCode",{parentName:"p"},"step()"),"\npermits more customized interactions (e.g. tensorboard callbacks)."),(0,t.mdx)("h2",{id:"autoguides"},"AutoGuides"),(0,t.mdx)("p",null,"Manually defining a guide for each random variable can become tedious.\n",(0,t.mdx)("a",{parentName:"p",href:"https://beanmachine.org/api/beanmachine.ppl.inference.vi.autoguide.html#beanmachine.ppl.inference.vi.autoguide.AutoGuideVI"},(0,t.mdx)("inlineCode",{parentName:"a"},"AutoGuideVI")),"\nprovides an initialization strategy for ",(0,t.mdx)("inlineCode",{parentName:"p"},"VariationalInfer")," which\nautomatically defines guides through calling a method\n",(0,t.mdx)("inlineCode",{parentName:"p"},"get_guide(query: RVIdentifier, distrib: dist.Distribution)")," implemented by\nsubclasses."),(0,t.mdx)("p",null,"All ",(0,t.mdx)("inlineCode",{parentName:"p"},"AutoGuide"),"s currently make a mean-field assumption over ",(0,t.mdx)("inlineCode",{parentName:"p"},"RVIdentifiers"),":\n",(0,t.mdx)("span",{parentName:"p",className:"math math-inline"},(0,t.mdx)("span",{parentName:"span",className:"katex"},(0,t.mdx)("span",{parentName:"span",className:"katex-mathml"},(0,t.mdx)("math",{parentName:"span",xmlns:"http://www.w3.org/1998/Math/MathML"},(0,t.mdx)("semantics",{parentName:"math"},(0,t.mdx)("mrow",{parentName:"semantics"},(0,t.mdx)("mi",{parentName:"mrow"},"q"),(0,t.mdx)("mo",{parentName:"mrow",stretchy:"false"},"("),(0,t.mdx)("mi",{parentName:"mrow"},"x"),(0,t.mdx)("mo",{parentName:"mrow",stretchy:"false"},")"),(0,t.mdx)("mo",{parentName:"mrow"},"="),(0,t.mdx)("msub",{parentName:"mrow"},(0,t.mdx)("mo",{parentName:"msub"},"\u220f"),(0,t.mdx)("mrow",{parentName:"msub"},(0,t.mdx)("mi",{parentName:"mrow"},"i"),(0,t.mdx)("mo",{parentName:"mrow"},"\u2208"),(0,t.mdx)("mtext",{parentName:"mrow"},"RVIDs"))),(0,t.mdx)("msub",{parentName:"mrow"},(0,t.mdx)("mi",{parentName:"msub"},"q"),(0,t.mdx)("mi",{parentName:"msub"},"i")),(0,t.mdx)("mo",{parentName:"mrow",stretchy:"false"},"("),(0,t.mdx)("msub",{parentName:"mrow"},(0,t.mdx)("mi",{parentName:"msub"},"x"),(0,t.mdx)("mi",{parentName:"msub"},"i")),(0,t.mdx)("mo",{parentName:"mrow",stretchy:"false"},")")),(0,t.mdx)("annotation",{parentName:"semantics",encoding:"application/x-tex"},"q(x) = \\prod_{i \\in \\text{RVIDs}} q_i(x_i)")))),(0,t.mdx)("span",{parentName:"span",className:"katex-html","aria-hidden":"true"},(0,t.mdx)("span",{parentName:"span",className:"base"},(0,t.mdx)("span",{parentName:"span",className:"strut",style:{height:"1em",verticalAlign:"-0.25em"}}),(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal",style:{marginRight:"0.03588em"}},"q"),(0,t.mdx)("span",{parentName:"span",className:"mopen"},"("),(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal"},"x"),(0,t.mdx)("span",{parentName:"span",className:"mclose"},")"),(0,t.mdx)("span",{parentName:"span",className:"mspace",style:{marginRight:"0.2777777777777778em"}}),(0,t.mdx)("span",{parentName:"span",className:"mrel"},"="),(0,t.mdx)("span",{parentName:"span",className:"mspace",style:{marginRight:"0.2777777777777778em"}})),(0,t.mdx)("span",{parentName:"span",className:"base"},(0,t.mdx)("span",{parentName:"span",className:"strut",style:{height:"1.07708em",verticalAlign:"-0.32708000000000004em"}}),(0,t.mdx)("span",{parentName:"span",className:"mop"},(0,t.mdx)("span",{parentName:"span",className:"mop op-symbol small-op",style:{position:"relative",top:"-0.0000050000000000050004em"}},"\u220f"),(0,t.mdx)("span",{parentName:"span",className:"msupsub"},(0,t.mdx)("span",{parentName:"span",className:"vlist-t vlist-t2"},(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.17862099999999992em"}},(0,t.mdx)("span",{parentName:"span",style:{top:"-2.40029em",marginLeft:"0em",marginRight:"0.05em"}},(0,t.mdx)("span",{parentName:"span",className:"pstrut",style:{height:"2.7em"}}),(0,t.mdx)("span",{parentName:"span",className:"sizing reset-size6 size3 mtight"},(0,t.mdx)("span",{parentName:"span",className:"mord mtight"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal mtight"},"i"),(0,t.mdx)("span",{parentName:"span",className:"mrel mtight"},"\u2208"),(0,t.mdx)("span",{parentName:"span",className:"mord text mtight"},(0,t.mdx)("span",{parentName:"span",className:"mord mtight"},"RVIDs")))))),(0,t.mdx)("span",{parentName:"span",className:"vlist-s"},"\u200b")),(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.32708000000000004em"}},(0,t.mdx)("span",{parentName:"span"})))))),(0,t.mdx)("span",{parentName:"span",className:"mspace",style:{marginRight:"0.16666666666666666em"}}),(0,t.mdx)("span",{parentName:"span",className:"mord"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal",style:{marginRight:"0.03588em"}},"q"),(0,t.mdx)("span",{parentName:"span",className:"msupsub"},(0,t.mdx)("span",{parentName:"span",className:"vlist-t vlist-t2"},(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.31166399999999994em"}},(0,t.mdx)("span",{parentName:"span",style:{top:"-2.5500000000000003em",marginLeft:"-0.03588em",marginRight:"0.05em"}},(0,t.mdx)("span",{parentName:"span",className:"pstrut",style:{height:"2.7em"}}),(0,t.mdx)("span",{parentName:"span",className:"sizing reset-size6 size3 mtight"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal mtight"},"i")))),(0,t.mdx)("span",{parentName:"span",className:"vlist-s"},"\u200b")),(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.15em"}},(0,t.mdx)("span",{parentName:"span"})))))),(0,t.mdx)("span",{parentName:"span",className:"mopen"},"("),(0,t.mdx)("span",{parentName:"span",className:"mord"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal"},"x"),(0,t.mdx)("span",{parentName:"span",className:"msupsub"},(0,t.mdx)("span",{parentName:"span",className:"vlist-t vlist-t2"},(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.31166399999999994em"}},(0,t.mdx)("span",{parentName:"span",style:{top:"-2.5500000000000003em",marginLeft:"0em",marginRight:"0.05em"}},(0,t.mdx)("span",{parentName:"span",className:"pstrut",style:{height:"2.7em"}}),(0,t.mdx)("span",{parentName:"span",className:"sizing reset-size6 size3 mtight"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal mtight"},"i")))),(0,t.mdx)("span",{parentName:"span",className:"vlist-s"},"\u200b")),(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.15em"}},(0,t.mdx)("span",{parentName:"span"})))))),(0,t.mdx)("span",{parentName:"span",className:"mclose"},")")))))),(0,t.mdx)("h3",{id:"advi"},"ADVI"),(0,t.mdx)("p",null,"In Automatic Differentiation Variational Inference (ADVI),\na properly-sized Gaussian is used as a guide to approximate each site:\n",(0,t.mdx)("span",{parentName:"p",className:"math math-inline"},(0,t.mdx)("span",{parentName:"span",className:"katex"},(0,t.mdx)("span",{parentName:"span",className:"katex-mathml"},(0,t.mdx)("math",{parentName:"span",xmlns:"http://www.w3.org/1998/Math/MathML"},(0,t.mdx)("semantics",{parentName:"math"},(0,t.mdx)("mrow",{parentName:"semantics"},(0,t.mdx)("msub",{parentName:"mrow"},(0,t.mdx)("mi",{parentName:"msub"},"q"),(0,t.mdx)("mi",{parentName:"msub"},"i")),(0,t.mdx)("mo",{parentName:"mrow"},"\u223c"),(0,t.mdx)("mi",{parentName:"mrow",mathvariant:"script"},"N"),(0,t.mdx)("mo",{parentName:"mrow",stretchy:"false"},"("),(0,t.mdx)("msub",{parentName:"mrow"},(0,t.mdx)("mi",{parentName:"msub"},"\u03bc"),(0,t.mdx)("mi",{parentName:"msub"},"i")),(0,t.mdx)("mo",{parentName:"mrow",separator:"true"},","),(0,t.mdx)("msub",{parentName:"mrow"},(0,t.mdx)("mi",{parentName:"msub"},"\u03c3"),(0,t.mdx)("mi",{parentName:"msub"},"i")),(0,t.mdx)("mo",{parentName:"mrow",stretchy:"false"},")")),(0,t.mdx)("annotation",{parentName:"semantics",encoding:"application/x-tex"},"q_i \\sim \\mathcal{N}(\\mu_i, \\sigma_i)")))),(0,t.mdx)("span",{parentName:"span",className:"katex-html","aria-hidden":"true"},(0,t.mdx)("span",{parentName:"span",className:"base"},(0,t.mdx)("span",{parentName:"span",className:"strut",style:{height:"0.625em",verticalAlign:"-0.19444em"}}),(0,t.mdx)("span",{parentName:"span",className:"mord"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal",style:{marginRight:"0.03588em"}},"q"),(0,t.mdx)("span",{parentName:"span",className:"msupsub"},(0,t.mdx)("span",{parentName:"span",className:"vlist-t vlist-t2"},(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.31166399999999994em"}},(0,t.mdx)("span",{parentName:"span",style:{top:"-2.5500000000000003em",marginLeft:"-0.03588em",marginRight:"0.05em"}},(0,t.mdx)("span",{parentName:"span",className:"pstrut",style:{height:"2.7em"}}),(0,t.mdx)("span",{parentName:"span",className:"sizing reset-size6 size3 mtight"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal mtight"},"i")))),(0,t.mdx)("span",{parentName:"span",className:"vlist-s"},"\u200b")),(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.15em"}},(0,t.mdx)("span",{parentName:"span"})))))),(0,t.mdx)("span",{parentName:"span",className:"mspace",style:{marginRight:"0.2777777777777778em"}}),(0,t.mdx)("span",{parentName:"span",className:"mrel"},"\u223c"),(0,t.mdx)("span",{parentName:"span",className:"mspace",style:{marginRight:"0.2777777777777778em"}})),(0,t.mdx)("span",{parentName:"span",className:"base"},(0,t.mdx)("span",{parentName:"span",className:"strut",style:{height:"1em",verticalAlign:"-0.25em"}}),(0,t.mdx)("span",{parentName:"span",className:"mord"},(0,t.mdx)("span",{parentName:"span",className:"mord mathcal",style:{marginRight:"0.14736em"}},"N")),(0,t.mdx)("span",{parentName:"span",className:"mopen"},"("),(0,t.mdx)("span",{parentName:"span",className:"mord"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal"},"\u03bc"),(0,t.mdx)("span",{parentName:"span",className:"msupsub"},(0,t.mdx)("span",{parentName:"span",className:"vlist-t vlist-t2"},(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.31166399999999994em"}},(0,t.mdx)("span",{parentName:"span",style:{top:"-2.5500000000000003em",marginLeft:"0em",marginRight:"0.05em"}},(0,t.mdx)("span",{parentName:"span",className:"pstrut",style:{height:"2.7em"}}),(0,t.mdx)("span",{parentName:"span",className:"sizing reset-size6 size3 mtight"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal mtight"},"i")))),(0,t.mdx)("span",{parentName:"span",className:"vlist-s"},"\u200b")),(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.15em"}},(0,t.mdx)("span",{parentName:"span"})))))),(0,t.mdx)("span",{parentName:"span",className:"mpunct"},","),(0,t.mdx)("span",{parentName:"span",className:"mspace",style:{marginRight:"0.16666666666666666em"}}),(0,t.mdx)("span",{parentName:"span",className:"mord"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal",style:{marginRight:"0.03588em"}},"\u03c3"),(0,t.mdx)("span",{parentName:"span",className:"msupsub"},(0,t.mdx)("span",{parentName:"span",className:"vlist-t vlist-t2"},(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.31166399999999994em"}},(0,t.mdx)("span",{parentName:"span",style:{top:"-2.5500000000000003em",marginLeft:"-0.03588em",marginRight:"0.05em"}},(0,t.mdx)("span",{parentName:"span",className:"pstrut",style:{height:"2.7em"}}),(0,t.mdx)("span",{parentName:"span",className:"sizing reset-size6 size3 mtight"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal mtight"},"i")))),(0,t.mdx)("span",{parentName:"span",className:"vlist-s"},"\u200b")),(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.15em"}},(0,t.mdx)("span",{parentName:"span"})))))),(0,t.mdx)("span",{parentName:"span",className:"mclose"},")")))))),(0,t.mdx)("h3",{id:"map"},"MAP"),(0,t.mdx)("p",null,"In Maximum A Posteriori (MAP) inference,\na ",(0,t.mdx)("a",{parentName:"p",href:"https://beanmachine.org/api/beanmachine.ppl.distributions.html#beanmachine.ppl.distributions.Delta"},(0,t.mdx)("inlineCode",{parentName:"a"},"Delta")),"\npoint estimate is used as the guide for each site:\n",(0,t.mdx)("span",{parentName:"p",className:"math math-inline"},(0,t.mdx)("span",{parentName:"span",className:"katex"},(0,t.mdx)("span",{parentName:"span",className:"katex-mathml"},(0,t.mdx)("math",{parentName:"span",xmlns:"http://www.w3.org/1998/Math/MathML"},(0,t.mdx)("semantics",{parentName:"math"},(0,t.mdx)("mrow",{parentName:"semantics"},(0,t.mdx)("msub",{parentName:"mrow"},(0,t.mdx)("mi",{parentName:"msub"},"q"),(0,t.mdx)("mi",{parentName:"msub"},"i")),(0,t.mdx)("mo",{parentName:"mrow"},"\u223c"),(0,t.mdx)("mtext",{parentName:"mrow"},"Delta"),(0,t.mdx)("mo",{parentName:"mrow",stretchy:"false"},"("),(0,t.mdx)("msub",{parentName:"mrow"},(0,t.mdx)("mi",{parentName:"msub"},"\u03bc"),(0,t.mdx)("mi",{parentName:"msub"},"i")),(0,t.mdx)("mo",{parentName:"mrow",stretchy:"false"},")")),(0,t.mdx)("annotation",{parentName:"semantics",encoding:"application/x-tex"},"q_i \\sim \\text{Delta}(\\mu_i)")))),(0,t.mdx)("span",{parentName:"span",className:"katex-html","aria-hidden":"true"},(0,t.mdx)("span",{parentName:"span",className:"base"},(0,t.mdx)("span",{parentName:"span",className:"strut",style:{height:"0.625em",verticalAlign:"-0.19444em"}}),(0,t.mdx)("span",{parentName:"span",className:"mord"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal",style:{marginRight:"0.03588em"}},"q"),(0,t.mdx)("span",{parentName:"span",className:"msupsub"},(0,t.mdx)("span",{parentName:"span",className:"vlist-t vlist-t2"},(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.31166399999999994em"}},(0,t.mdx)("span",{parentName:"span",style:{top:"-2.5500000000000003em",marginLeft:"-0.03588em",marginRight:"0.05em"}},(0,t.mdx)("span",{parentName:"span",className:"pstrut",style:{height:"2.7em"}}),(0,t.mdx)("span",{parentName:"span",className:"sizing reset-size6 size3 mtight"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal mtight"},"i")))),(0,t.mdx)("span",{parentName:"span",className:"vlist-s"},"\u200b")),(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.15em"}},(0,t.mdx)("span",{parentName:"span"})))))),(0,t.mdx)("span",{parentName:"span",className:"mspace",style:{marginRight:"0.2777777777777778em"}}),(0,t.mdx)("span",{parentName:"span",className:"mrel"},"\u223c"),(0,t.mdx)("span",{parentName:"span",className:"mspace",style:{marginRight:"0.2777777777777778em"}})),(0,t.mdx)("span",{parentName:"span",className:"base"},(0,t.mdx)("span",{parentName:"span",className:"strut",style:{height:"1em",verticalAlign:"-0.25em"}}),(0,t.mdx)("span",{parentName:"span",className:"mord text"},(0,t.mdx)("span",{parentName:"span",className:"mord"},"Delta")),(0,t.mdx)("span",{parentName:"span",className:"mopen"},"("),(0,t.mdx)("span",{parentName:"span",className:"mord"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal"},"\u03bc"),(0,t.mdx)("span",{parentName:"span",className:"msupsub"},(0,t.mdx)("span",{parentName:"span",className:"vlist-t vlist-t2"},(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.31166399999999994em"}},(0,t.mdx)("span",{parentName:"span",style:{top:"-2.5500000000000003em",marginLeft:"0em",marginRight:"0.05em"}},(0,t.mdx)("span",{parentName:"span",className:"pstrut",style:{height:"2.7em"}}),(0,t.mdx)("span",{parentName:"span",className:"sizing reset-size6 size3 mtight"},(0,t.mdx)("span",{parentName:"span",className:"mord mathnormal mtight"},"i")))),(0,t.mdx)("span",{parentName:"span",className:"vlist-s"},"\u200b")),(0,t.mdx)("span",{parentName:"span",className:"vlist-r"},(0,t.mdx)("span",{parentName:"span",className:"vlist",style:{height:"0.15em"}},(0,t.mdx)("span",{parentName:"span"})))))),(0,t.mdx)("span",{parentName:"span",className:"mclose"},")")))))))}c.isMDXComponent=!0}}]);