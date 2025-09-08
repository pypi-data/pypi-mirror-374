/*      Compiler: ECL 24.5.10                                         */
/*      Date: 2025/9/7 10:16 (yyyy/mm/dd)                             */
/*      Machine: Darwin 23.6.0 arm64                                  */
/*      Source: /Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/pre-generated/src/algebra/ISTRING.lsp */
#include <ecl/ecl-cmp.h>
#include "/Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/_build/target/aarch64-apple-darwin23.6.0/algebra/ISTRING.eclh"
/*      function definition for ISTRING;new;NniC%;1                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1065_istring_new_nnic__1_(cl_object v1_n_, cl_object v2_c_, cl_object v3_)
{
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 value0 = ecl_function_dispatch(cl_env_copy,VV[2])(2, v1_n_, v2_c_) /*  make_string_code */;
 return value0;
}
/*      function definition for ISTRING;empty;%;2                     */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1066_istring_empty___2_(cl_object v1_)
{
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 value0 = ecl_function_dispatch(cl_env_copy,VV[61])(1, ecl_make_fixnum(0)) /*  filler_spaces */;
 return value0;
}
/*      function definition for ISTRING;empty?;%B;3                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1067_istring_empty___b_3_(cl_object v1_s_, cl_object v2_)
{
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_fixnum v3;
  v3 = (v1_s_)->vector.fillp;
  value0 = ecl_make_bool((v3)==(0));
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for ISTRING;#;%Nni;4                      */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1068_istring____nni_4_(cl_object v1_s_, cl_object v2_)
{
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 value0 = ecl_make_fixnum((v1_s_)->vector.fillp);
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for ISTRING;=;2%B;5                       */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1069_istring___2_b_5_(cl_object v1_s_, cl_object v2_t_, cl_object v3_)
{
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 value0 = ecl_make_bool(ecl_equal(v1_s_,v2_t_));
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for ISTRING;<;2%B;6                       */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1070_istring___2_b_6_(cl_object v1_s_, cl_object v2_t_, cl_object v3_)
{
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 value0 = ecl_function_dispatch(cl_env_copy,VV[66])(2, v2_t_, v1_s_) /*  CGREATERP */;
 return value0;
}
/*      function definition for ISTRING;concat;3%;7                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1071_istring_concat_3__7_(cl_object v1_s_, cl_object v2_t_, cl_object v3_)
{
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 value0 = ecl_function_dispatch(cl_env_copy,VV[10])(2, v1_s_, v2_t_) /*  STRCONC */;
 return value0;
}
/*      function definition for ISTRING;copy;2%;8                     */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1072_istring_copy_2__8_(cl_object v1_s_, cl_object v2_)
{
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 value0 = ecl_copy_seq(v1_s_);
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for ISTRING;insert;2%I%;9                 */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1073_istring_insert_2_i__9_(cl_object v1_s_, cl_object v2_t_, cl_object v3_i_, cl_object v4_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6, T7, T8, T9;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[16];
  T0 = _ecl_car(v5);
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[16];
   T2 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v4_)->vector.self.t[21];
    T4 = _ecl_car(v7);
    {
     cl_object v8;
     v8 = (v4_)->vector.self.t[20];
     T6 = _ecl_car(v8);
     T7 = (v4_)->vector.self.t[6];
     T8 = ecl_minus(v3_i_,ecl_make_fixnum(1));
     T9 = _ecl_cdr(v8);
     T5 = (cl_env_copy->function=T6)->cfun.entry(3, T7, T8, T9);
    }
    T6 = _ecl_cdr(v7);
    T3 = (cl_env_copy->function=T4)->cfun.entry(3, v1_s_, T5, T6);
   }
   T4 = _ecl_cdr(v6);
   T1 = (cl_env_copy->function=T2)->cfun.entry(3, T3, v2_t_, T4);
  }
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[21];
   T3 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v4_)->vector.self.t[22];
    T5 = _ecl_car(v7);
    T6 = _ecl_cdr(v7);
    T4 = (cl_env_copy->function=T5)->cfun.entry(2, v3_i_, T6);
   }
   T5 = _ecl_cdr(v6);
   T2 = (cl_env_copy->function=T3)->cfun.entry(3, v1_s_, T4, T5);
  }
  T3 = _ecl_cdr(v5);
  value0 = (cl_env_copy->function=T0)->cfun.entry(3, T1, T2, T3);
  return value0;
 }
}
/*      function definition for ISTRING;coerce;%Of;10                 */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1074_istring_coerce__of_10_(cl_object v1_s_, cl_object v2_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  v3 = (v2_)->vector.self.t[26];
  T0 = _ecl_car(v3);
  T1 = _ecl_cdr(v3);
  value0 = (cl_env_copy->function=T0)->cfun.entry(2, v1_s_, T1);
  return value0;
 }
}
/*      function definition for ISTRING;minIndex;%I;11                */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1075_istring_minindex__i_11_(cl_object v1_s_, cl_object v2_)
{
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 value0 = (v2_)->vector.self.t[6];
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for ISTRING;upperCase!;2%;12              */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1076_istring_uppercase__2__12_(cl_object v1_s_, cl_object v2_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  v3 = (v2_)->vector.self.t[33];
  T0 = _ecl_car(v3);
  T1 = ecl_elt(v2_,31);
  T2 = _ecl_cdr(v3);
  value0 = (cl_env_copy->function=T0)->cfun.entry(3, T1, v1_s_, T2);
  return value0;
 }
}
/*      function definition for ISTRING;lowerCase!;2%;13              */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1077_istring_lowercase__2__13_(cl_object v1_s_, cl_object v2_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  v3 = (v2_)->vector.self.t[33];
  T0 = _ecl_car(v3);
  T1 = ecl_elt(v2_,36);
  T2 = _ecl_cdr(v3);
  value0 = (cl_env_copy->function=T0)->cfun.entry(3, T1, v1_s_, T2);
  return value0;
 }
}
/*      function definition for ISTRING;replace;%Us2%;14              */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1078_istring_replace__us2__14_(cl_object v1_s_, cl_object v2_sg_, cl_object v3_t_, cl_object v4_)
{
 cl_object T0, T1, T2, T3, T4;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5_k_;
  cl_object v6;
  cl_object v7_i_;
  cl_object v8;
  cl_object v9;
  cl_object v10_r_;
  cl_object v11;
  cl_object v12_h_;
  cl_object v13_n_;
  cl_object v14_m_;
  cl_object v15_l_;
  v5_k_ = ECL_NIL;
  v6 = ECL_NIL;
  v7_i_ = ECL_NIL;
  v8 = ECL_NIL;
  v9 = ECL_NIL;
  v10_r_ = ECL_NIL;
  v11 = ECL_NIL;
  v12_h_ = ecl_make_fixnum(0);
  v13_n_ = ecl_make_fixnum(0);
  v14_m_ = ecl_make_fixnum(0);
  v15_l_ = ecl_make_fixnum(0);
  {
   cl_object v16;
   v16 = (v4_)->vector.self.t[38];
   T1 = _ecl_car(v16);
   T2 = _ecl_cdr(v16);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v2_sg_, T2);
  }
  T1 = (v4_)->vector.self.t[6];
  v15_l_ = ecl_minus(T0,T1);
  {
   cl_object v16;
   v16 = (v4_)->vector.self.t[13];
   T0 = _ecl_car(v16);
   T1 = _ecl_cdr(v16);
   v14_m_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_s_, T1);
  }
  {
   cl_object v16;
   v16 = (v4_)->vector.self.t[13];
   T0 = _ecl_car(v16);
   T1 = _ecl_cdr(v16);
   v13_n_ = (cl_env_copy->function=T0)->cfun.entry(2, v3_t_, T1);
  }
  {
   cl_object v16;
   v16 = (v4_)->vector.self.t[39];
   T0 = _ecl_car(v16);
   T1 = _ecl_cdr(v16);
   if (Null((cl_env_copy->function=T0)->cfun.entry(2, v2_sg_, T1))) { goto L27; }
  }
  {
   cl_object v16;
   v16 = (v4_)->vector.self.t[40];
   T1 = _ecl_car(v16);
   T2 = _ecl_cdr(v16);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v2_sg_, T2);
  }
  T1 = (v4_)->vector.self.t[6];
  v12_h_ = ecl_minus(T0,T1);
  goto L26;
L27:;
  {
   cl_object v16;
   v16 = (v4_)->vector.self.t[41];
   T1 = _ecl_car(v16);
   T2 = _ecl_cdr(v16);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v1_s_, T2);
  }
  T1 = (v4_)->vector.self.t[6];
  v12_h_ = ecl_minus(T0,T1);
L26:;
  if (ecl_lower(v15_l_,ecl_make_fixnum(0))) { goto L39; }
  if (ecl_greatereq(v12_h_,v14_m_)) { goto L39; }
  T0 = ecl_minus(v15_l_,ecl_make_fixnum(1));
  if (!(ecl_lower(v12_h_,T0))) { goto L37; }
  goto L38;
L39:;
L38:;
  value0 = ecl_function_dispatch(cl_env_copy,VV[75])(1, VV[18]) /*  error */;
  return value0;
L37:;
  {
   cl_object v16;
   v16 = (v4_)->vector.self.t[9];
   T0 = _ecl_car(v16);
   {
    cl_object v17;
    T2 = ecl_minus(v12_h_,v15_l_);
    T3 = ecl_plus(T2,ecl_make_fixnum(1));
    T4 = ecl_minus(v14_m_,T3);
    v11 = ecl_plus(T4,v13_n_);
    v17 = v11;
    {
     bool v18;
     v18 = ecl_greatereq(v11,ecl_make_fixnum(0));
     if (!(ecl_make_bool(v18)==ECL_NIL)) { goto L49; }
    }
    T2 = ecl_function_dispatch(cl_env_copy,VV[76])(3, v11, VV[19], VV[20]) /*  coerce_failure_msg */;
    ecl_function_dispatch(cl_env_copy,VV[75])(1, T2) /*  error        */;
L49:;
    T1 = v17;
   }
   {
    cl_object v17;
    v17 = (v4_)->vector.self.t[42];
    T3 = _ecl_car(v17);
    T4 = _ecl_cdr(v17);
    T2 = (cl_env_copy->function=T3)->cfun.entry(1, T4);
   }
   T3 = _ecl_cdr(v16);
   v10_r_ = (cl_env_copy->function=T0)->cfun.entry(3, T1, T2, T3);
  }
  v7_i_ = ecl_make_fixnum(0);
  v9 = ecl_minus(v15_l_,ecl_make_fixnum(1));
  v5_k_ = ecl_make_fixnum(0);
L55:;
  if (!((ecl_fixnum(v7_i_))>(ecl_fixnum(v9)))) { goto L63; }
  goto L56;
L63:;
  {
   cl_fixnum v16;
   {
    ecl_character v17;
    v17 = ecl_char(v1_s_,ecl_fixnum(v7_i_));
    v16 = v17;
   }
   {
    ecl_character v17;
    v17 = v16;
    ecl_char_set(v10_r_,ecl_fixnum(v5_k_),v17);
   }
   goto L65;
  }
L65:;
  {
   cl_fixnum v16;
   v16 = (ecl_fixnum(v5_k_))+1;
   v7_i_ = ecl_make_fixnum((ecl_fixnum(v7_i_))+1);
   v5_k_ = ecl_make_fixnum(v16);
  }
  goto L55;
L56:;
  goto L54;
L54:;
  v7_i_ = ecl_make_fixnum(0);
  v8 = ecl_minus(v13_n_,ecl_make_fixnum(1));
L77:;
  if (!((ecl_fixnum(v7_i_))>(ecl_fixnum(v8)))) { goto L85; }
  goto L78;
L85:;
  {
   cl_fixnum v16;
   {
    ecl_character v17;
    v17 = ecl_char(v3_t_,ecl_fixnum(v7_i_));
    v16 = v17;
   }
   {
    ecl_character v17;
    v17 = v16;
    ecl_char_set(v10_r_,ecl_fixnum(v5_k_),v17);
   }
   goto L87;
  }
L87:;
  {
   cl_object v16;
   v16 = ecl_plus(v5_k_,ecl_make_fixnum(1));
   v7_i_ = ecl_make_fixnum((ecl_fixnum(v7_i_))+1);
   v5_k_ = v16;
  }
  goto L77;
L78:;
  goto L76;
L76:;
  v7_i_ = ecl_plus(v12_h_,ecl_make_fixnum(1));
  v6 = ecl_minus(v14_m_,ecl_make_fixnum(1));
L99:;
  if (!(ecl_greater(v7_i_,v6))) { goto L107; }
  goto L100;
L107:;
  {
   cl_fixnum v16;
   {
    ecl_character v17;
    v17 = ecl_char(v1_s_,ecl_fixnum(v7_i_));
    v16 = v17;
   }
   {
    ecl_character v17;
    v17 = v16;
    ecl_char_set(v10_r_,ecl_fixnum(v5_k_),v17);
   }
   goto L109;
  }
L109:;
  {
   cl_object v16;
   v16 = ecl_plus(v5_k_,ecl_make_fixnum(1));
   v7_i_ = ecl_plus(v7_i_,ecl_make_fixnum(1));
   v5_k_ = v16;
  }
  goto L99;
L100:;
  goto L98;
L98:;
  value0 = v10_r_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for ISTRING;qsetelt!;%I2C;15              */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1079_istring_qsetelt___i2c_15_(cl_object v1_s_, cl_object v2_i_, cl_object v3_c_, cl_object v4_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = (v4_)->vector.self.t[6];
 T1 = ecl_minus(v2_i_,T0);
 {
  ecl_character v5;
  v5 = ecl_fixnum(v3_c_);
  ecl_char_set(v1_s_,ecl_fixnum(T1),v5);
 }
 value0 = v3_c_;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for ISTRING;setelt!;%I2C;16               */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1080_istring_setelt___i2c_16_(cl_object v1_s_, cl_object v2_i_, cl_object v3_c_, cl_object v4_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = (v4_)->vector.self.t[6];
 if (ecl_lower(v2_i_,T0)) { goto L3; }
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[41];
  T1 = _ecl_car(v5);
  T2 = _ecl_cdr(v5);
  T0 = (cl_env_copy->function=T1)->cfun.entry(2, v1_s_, T2);
 }
 if (!(ecl_greater(v2_i_,T0))) { goto L1; }
 goto L2;
L3:;
L2:;
 value0 = ecl_function_dispatch(cl_env_copy,VV[75])(1, VV[18]) /*  error */;
 return value0;
L1:;
 T0 = (v4_)->vector.self.t[6];
 T1 = ecl_minus(v2_i_,T0);
 {
  ecl_character v5;
  v5 = ecl_fixnum(v3_c_);
  ecl_char_set(v1_s_,ecl_fixnum(T1),v5);
 }
 value0 = v3_c_;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for ISTRING;substring?;2%IB;17            */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1081_istring_substring__2_ib_17_(cl_object v1_part_, cl_object v2_whole_, cl_object v3_startpos_, cl_object v4_)
{
 cl_object T0;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5;
  cl_object v6;
  cl_object v7;
  cl_object v8_ip_;
  cl_object v9_iw_;
  cl_object v10_nw_;
  cl_object v11_np_;
  v5 = ECL_NIL;
  v6 = ECL_NIL;
  v7 = ECL_NIL;
  v8_ip_ = ECL_NIL;
  v9_iw_ = ECL_NIL;
  v10_nw_ = ecl_make_fixnum(0);
  v11_np_ = ecl_make_fixnum(0);
  v11_np_ = ecl_make_fixnum((v1_part_)->vector.fillp);
  v10_nw_ = ecl_make_fixnum((v2_whole_)->vector.fillp);
  T0 = (v4_)->vector.self.t[6];
  v3_startpos_ = ecl_minus(v3_startpos_,T0);
  if (!(ecl_lower(v3_startpos_,ecl_make_fixnum(0)))) { goto L17; }
  value0 = ecl_function_dispatch(cl_env_copy,VV[75])(1, VV[24]) /*  error */;
  return value0;
L17:;
  T0 = ecl_minus(v10_nw_,v3_startpos_);
  if (!(ecl_greater(v11_np_,T0))) { goto L19; }
  value0 = ECL_NIL;
  cl_env_copy->nvalues = 1;
  return value0;
L19:;
  v9_iw_ = v3_startpos_;
  v8_ip_ = ecl_make_fixnum(0);
  v7 = ecl_minus(v11_np_,ecl_make_fixnum(1));
L24:;
  if (!((ecl_fixnum(v8_ip_))>(ecl_fixnum(v7)))) { goto L32; }
  goto L25;
L32:;
  {
   ecl_character v12;
   v12 = ecl_char(v1_part_,ecl_fixnum(v8_ip_));
   {
    cl_fixnum v13;
    v13 = v12;
    {
     ecl_character v14;
     v14 = ecl_char(v2_whole_,ecl_fixnum(v9_iw_));
     {
      cl_fixnum v15;
      v15 = v14;
      {
       bool v16;
       v16 = (v13)==(v15);
       if (!(ecl_make_bool(v16)==ECL_NIL)) { goto L34; }
      }
     }
    }
   }
  }
  v6 = ECL_NIL;
  goto L8;
  goto L22;
L34:;
  {
   cl_fixnum v12;
   v12 = (ecl_fixnum(v8_ip_))+1;
   v9_iw_ = ecl_plus(v9_iw_,ecl_make_fixnum(1));
   v8_ip_ = ecl_make_fixnum(v12);
  }
  goto L24;
L25:;
  goto L21;
L22:;
  goto L21;
L21:;
  value0 = ECL_T;
  cl_env_copy->nvalues = 1;
  return value0;
L8:;
  value0 = v6;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for ISTRING;position;2%2I;18              */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1082_istring_position_2_2i_18_(cl_object v1_s_, cl_object v2_t_, cl_object v3_startpos_, cl_object v4_)
{
 cl_object T0;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5_r_;
  v5_r_ = ECL_NIL;
  T0 = (v4_)->vector.self.t[6];
  v3_startpos_ = ecl_minus(v3_startpos_,T0);
  if (!(ecl_lower(v3_startpos_,ecl_make_fixnum(0)))) { goto L5; }
  value0 = ecl_function_dispatch(cl_env_copy,VV[75])(1, VV[24]) /*  error */;
  return value0;
L5:;
  {
   cl_fixnum v6;
   v6 = (v2_t_)->vector.fillp;
   if (!(ecl_greatereq(v3_startpos_,ecl_make_fixnum(v6)))) { goto L7; }
  }
  T0 = (v4_)->vector.self.t[6];
  value0 = ecl_minus(T0,ecl_make_fixnum(1));
  cl_env_copy->nvalues = 1;
  return value0;
L7:;
  v5_r_ = ecl_function_dispatch(cl_env_copy,VV[81])(4, v1_s_, v2_t_, v3_startpos_, ECL_NIL) /*  STRPOS */;
  if (!((v5_r_)==(ECL_NIL))) { goto L12; }
  T0 = (v4_)->vector.self.t[6];
  value0 = ecl_minus(T0,ecl_make_fixnum(1));
  cl_env_copy->nvalues = 1;
  return value0;
L12:;
  T0 = (v4_)->vector.self.t[6];
  value0 = ecl_plus(v5_r_,T0);
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for ISTRING;position;C%2I;19              */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1083_istring_position_c_2i_19_(cl_object v1_c_, cl_object v2_t_, cl_object v3_startpos_, cl_object v4_)
{
 cl_object T0;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5;
  cl_object v6;
  cl_object v7_r_;
  v5 = ECL_NIL;
  v6 = ECL_NIL;
  v7_r_ = ECL_NIL;
  T0 = (v4_)->vector.self.t[6];
  v3_startpos_ = ecl_minus(v3_startpos_,T0);
  if (!(ecl_lower(v3_startpos_,ecl_make_fixnum(0)))) { goto L9; }
  value0 = ecl_function_dispatch(cl_env_copy,VV[75])(1, VV[24]) /*  error */;
  return value0;
L9:;
  {
   cl_fixnum v8;
   v8 = (v2_t_)->vector.fillp;
   if (!(ecl_greatereq(v3_startpos_,ecl_make_fixnum(v8)))) { goto L11; }
  }
  T0 = (v4_)->vector.self.t[6];
  value0 = ecl_minus(T0,ecl_make_fixnum(1));
  cl_env_copy->nvalues = 1;
  return value0;
L11:;
  v7_r_ = v3_startpos_;
  {
   cl_fixnum v8;
   v8 = (v2_t_)->vector.fillp;
   v6 = ecl_make_fixnum((v8)-(1));
  }
L14:;
  if (!(ecl_greater(v7_r_,v6))) { goto L20; }
  goto L15;
L20:;
  {
   ecl_character v8;
   v8 = ecl_char(v2_t_,ecl_fixnum(v7_r_));
   {
    cl_fixnum v9;
    v9 = v8;
    if (!((v9)==(ecl_fixnum(v1_c_)))) { goto L22; }
   }
  }
  T0 = (v4_)->vector.self.t[6];
  v5 = ecl_plus(v7_r_,T0);
  goto L4;
L22:;
  v7_r_ = ecl_plus(v7_r_,ecl_make_fixnum(1));
  goto L14;
L15:;
  goto L13;
L13:;
  T0 = (v4_)->vector.self.t[6];
  value0 = ecl_minus(T0,ecl_make_fixnum(1));
  cl_env_copy->nvalues = 1;
  return value0;
L4:;
  value0 = v5;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for ISTRING;position;Cc%2I;20             */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1084_istring_position_cc_2i_20_(cl_object v1_cc_, cl_object v2_t_, cl_object v3_startpos_, cl_object v4_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5;
  cl_object v6;
  cl_object v7_r_;
  v5 = ECL_NIL;
  v6 = ECL_NIL;
  v7_r_ = ECL_NIL;
  T0 = (v4_)->vector.self.t[6];
  v3_startpos_ = ecl_minus(v3_startpos_,T0);
  if (!(ecl_lower(v3_startpos_,ecl_make_fixnum(0)))) { goto L9; }
  value0 = ecl_function_dispatch(cl_env_copy,VV[75])(1, VV[24]) /*  error */;
  return value0;
L9:;
  {
   cl_fixnum v8;
   v8 = (v2_t_)->vector.fillp;
   if (!(ecl_greatereq(v3_startpos_,ecl_make_fixnum(v8)))) { goto L11; }
  }
  T0 = (v4_)->vector.self.t[6];
  value0 = ecl_minus(T0,ecl_make_fixnum(1));
  cl_env_copy->nvalues = 1;
  return value0;
L11:;
  v7_r_ = v3_startpos_;
  {
   cl_fixnum v8;
   v8 = (v2_t_)->vector.fillp;
   v6 = ecl_make_fixnum((v8)-(1));
  }
L14:;
  if (!(ecl_greater(v7_r_,v6))) { goto L20; }
  goto L15;
L20:;
  {
   cl_object v8;
   v8 = (v4_)->vector.self.t[49];
   T0 = _ecl_car(v8);
   {
    ecl_character v9;
    v9 = ecl_char(v2_t_,ecl_fixnum(v7_r_));
    {
     cl_fixnum v10;
     v10 = v9;
     T1 = _ecl_cdr(v8);
     if (Null((cl_env_copy->function=T0)->cfun.entry(3, ecl_make_fixnum(v10), v1_cc_, T1))) { goto L22; }
    }
   }
  }
  T0 = (v4_)->vector.self.t[6];
  v5 = ecl_plus(v7_r_,T0);
  goto L4;
L22:;
  v7_r_ = ecl_plus(v7_r_,ecl_make_fixnum(1));
  goto L14;
L15:;
  goto L13;
L13:;
  T0 = (v4_)->vector.self.t[6];
  value0 = ecl_minus(T0,ecl_make_fixnum(1));
  cl_env_copy->nvalues = 1;
  return value0;
L4:;
  value0 = v5;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for ISTRING;suffix?;2%B;21                */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1085_istring_suffix__2_b_21_(cl_object v1_s_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_n_;
  cl_object v5_m_;
  v4_n_ = ecl_make_fixnum(0);
  v5_m_ = ecl_make_fixnum(0);
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[41];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   v5_m_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_s_, T1);
  }
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[41];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   v4_n_ = (cl_env_copy->function=T0)->cfun.entry(2, v2_t_, T1);
  }
  if (!(ecl_greater(v5_m_,v4_n_))) { goto L12; }
  value0 = ECL_NIL;
  cl_env_copy->nvalues = 1;
  return value0;
L12:;
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[46];
   T0 = _ecl_car(v6);
   T1 = (v3_)->vector.self.t[6];
   T2 = ecl_plus(T1,v4_n_);
   T3 = ecl_minus(T2,v5_m_);
   T4 = _ecl_cdr(v6);
   value0 = (cl_env_copy->function=T0)->cfun.entry(4, v1_s_, v2_t_, T3, T4);
   return value0;
  }
 }
}
/*      function definition for ISTRING;split;%CL;22                  */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1086_istring_split__cl_22_(cl_object v1_s_, cl_object v2_c_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_l_;
  cl_object v5;
  cl_object v6_i_;
  cl_object v7_j_;
  cl_object v8;
  cl_object v9_n_;
  v4_l_ = ECL_NIL;
  v5 = ECL_NIL;
  v6_i_ = ECL_NIL;
  v7_j_ = ecl_make_fixnum(0);
  v8 = ECL_NIL;
  v9_n_ = ecl_make_fixnum(0);
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[41];
   T0 = _ecl_car(v10);
   T1 = _ecl_cdr(v10);
   v9_n_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_s_, T1);
  }
  v6_i_ = (v3_)->vector.self.t[6];
  v8 = v9_n_;
L12:;
  if (ecl_greater(v6_i_,v8)) { goto L20; }
  {
   cl_fixnum v10;
   {
    cl_object v11;
    v11 = (v3_)->vector.self.t[52];
    T0 = _ecl_car(v11);
    T1 = _ecl_cdr(v11);
    v10 = ecl_fixnum((cl_env_copy->function=T0)->cfun.entry(3, v1_s_, v6_i_, T1));
   }
   {
    bool v11;
    v11 = (v10)==(ecl_fixnum(v2_c_));
    if (!(ecl_make_bool(v11)==ECL_NIL)) { goto L18; }
    goto L19;
   }
  }
L20:;
L19:;
  goto L13;
L18:;
  goto L25;
L25:;
  v6_i_ = ecl_plus(v6_i_,ecl_make_fixnum(1));
  goto L12;
L13:;
  goto L11;
L11:;
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[54];
   T0 = _ecl_car(v10);
   T1 = _ecl_cdr(v10);
   v4_l_ = (cl_env_copy->function=T0)->cfun.entry(1, T1);
  }
L36:;
  if (!(ecl_lowereq(v6_i_,v9_n_))) { goto L41; }
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[48];
   T1 = _ecl_car(v10);
   T2 = _ecl_cdr(v10);
   v7_j_ = (cl_env_copy->function=T1)->cfun.entry(4, v2_c_, v1_s_, v6_i_, T2);
  }
  T1 = (v3_)->vector.self.t[6];
  T0 = ecl_make_bool(ecl_greatereq(v7_j_,T1));
  goto L40;
L41:;
  T0 = ECL_NIL;
L40:;
  if (!(T0==ECL_NIL)) { goto L38; }
  goto L37;
L38:;
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[55];
   T0 = _ecl_car(v10);
   {
    cl_object v11;
    v11 = (v3_)->vector.self.t[21];
    T2 = _ecl_car(v11);
    {
     cl_object v12;
     v12 = (v3_)->vector.self.t[20];
     T4 = _ecl_car(v12);
     T5 = ecl_minus(v7_j_,ecl_make_fixnum(1));
     T6 = _ecl_cdr(v12);
     T3 = (cl_env_copy->function=T4)->cfun.entry(3, v6_i_, T5, T6);
    }
    T4 = _ecl_cdr(v11);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, v1_s_, T3, T4);
   }
   T2 = _ecl_cdr(v10);
   v4_l_ = (cl_env_copy->function=T0)->cfun.entry(3, T1, v4_l_, T2);
  }
  v6_i_ = v7_j_;
  v5 = v9_n_;
L58:;
  if (ecl_greater(v6_i_,v5)) { goto L66; }
  {
   cl_fixnum v10;
   {
    cl_object v11;
    v11 = (v3_)->vector.self.t[52];
    T0 = _ecl_car(v11);
    T1 = _ecl_cdr(v11);
    v10 = ecl_fixnum((cl_env_copy->function=T0)->cfun.entry(3, v1_s_, v6_i_, T1));
   }
   {
    bool v11;
    v11 = (v10)==(ecl_fixnum(v2_c_));
    if (!(ecl_make_bool(v11)==ECL_NIL)) { goto L64; }
    goto L65;
   }
  }
L66:;
L65:;
  goto L59;
L64:;
  goto L71;
L71:;
  v6_i_ = ecl_plus(v6_i_,ecl_make_fixnum(1));
  goto L58;
L59:;
  goto L46;
L46:;
  goto L36;
L37:;
  goto L35;
L35:;
  if (!(ecl_lowereq(v6_i_,v9_n_))) { goto L80; }
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[55];
   T0 = _ecl_car(v10);
   {
    cl_object v11;
    v11 = (v3_)->vector.self.t[21];
    T2 = _ecl_car(v11);
    {
     cl_object v12;
     v12 = (v3_)->vector.self.t[20];
     T4 = _ecl_car(v12);
     T5 = _ecl_cdr(v12);
     T3 = (cl_env_copy->function=T4)->cfun.entry(3, v6_i_, v9_n_, T5);
    }
    T4 = _ecl_cdr(v11);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, v1_s_, T3, T4);
   }
   T2 = _ecl_cdr(v10);
   v4_l_ = (cl_env_copy->function=T0)->cfun.entry(3, T1, v4_l_, T2);
  }
L80:;
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[56];
   T0 = _ecl_car(v10);
   T1 = _ecl_cdr(v10);
   value0 = (cl_env_copy->function=T0)->cfun.entry(2, v4_l_, T1);
   return value0;
  }
 }
}
/*      function definition for ISTRING;split;%CcL;23                 */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1087_istring_split__ccl_23_(cl_object v1_s_, cl_object v2_cc_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_l_;
  cl_object v5;
  cl_object v6_i_;
  cl_object v7_j_;
  cl_object v8;
  cl_object v9_n_;
  v4_l_ = ECL_NIL;
  v5 = ECL_NIL;
  v6_i_ = ECL_NIL;
  v7_j_ = ecl_make_fixnum(0);
  v8 = ECL_NIL;
  v9_n_ = ecl_make_fixnum(0);
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[41];
   T0 = _ecl_car(v10);
   T1 = _ecl_cdr(v10);
   v9_n_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_s_, T1);
  }
  v6_i_ = (v3_)->vector.self.t[6];
  v8 = v9_n_;
L12:;
  if (ecl_greater(v6_i_,v8)) { goto L20; }
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[49];
   T1 = _ecl_car(v10);
   {
    cl_object v11;
    v11 = (v3_)->vector.self.t[52];
    T3 = _ecl_car(v11);
    T4 = _ecl_cdr(v11);
    T2 = (cl_env_copy->function=T3)->cfun.entry(3, v1_s_, v6_i_, T4);
   }
   T3 = _ecl_cdr(v10);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, T2, v2_cc_, T3);
  }
  if (!(T0==ECL_NIL)) { goto L18; }
  goto L19;
L20:;
L19:;
  goto L13;
L18:;
  goto L28;
L28:;
  v6_i_ = ecl_plus(v6_i_,ecl_make_fixnum(1));
  goto L12;
L13:;
  goto L11;
L11:;
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[54];
   T0 = _ecl_car(v10);
   T1 = _ecl_cdr(v10);
   v4_l_ = (cl_env_copy->function=T0)->cfun.entry(1, T1);
  }
L39:;
  if (!(ecl_lowereq(v6_i_,v9_n_))) { goto L44; }
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[50];
   T1 = _ecl_car(v10);
   T2 = _ecl_cdr(v10);
   v7_j_ = (cl_env_copy->function=T1)->cfun.entry(4, v2_cc_, v1_s_, v6_i_, T2);
  }
  T1 = (v3_)->vector.self.t[6];
  T0 = ecl_make_bool(ecl_greatereq(v7_j_,T1));
  goto L43;
L44:;
  T0 = ECL_NIL;
L43:;
  if (!(T0==ECL_NIL)) { goto L41; }
  goto L40;
L41:;
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[55];
   T0 = _ecl_car(v10);
   {
    cl_object v11;
    v11 = (v3_)->vector.self.t[21];
    T2 = _ecl_car(v11);
    {
     cl_object v12;
     v12 = (v3_)->vector.self.t[20];
     T4 = _ecl_car(v12);
     T5 = ecl_minus(v7_j_,ecl_make_fixnum(1));
     T6 = _ecl_cdr(v12);
     T3 = (cl_env_copy->function=T4)->cfun.entry(3, v6_i_, T5, T6);
    }
    T4 = _ecl_cdr(v11);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, v1_s_, T3, T4);
   }
   T2 = _ecl_cdr(v10);
   v4_l_ = (cl_env_copy->function=T0)->cfun.entry(3, T1, v4_l_, T2);
  }
  v6_i_ = v7_j_;
  v5 = v9_n_;
L61:;
  if (ecl_greater(v6_i_,v5)) { goto L69; }
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[49];
   T1 = _ecl_car(v10);
   {
    cl_object v11;
    v11 = (v3_)->vector.self.t[52];
    T3 = _ecl_car(v11);
    T4 = _ecl_cdr(v11);
    T2 = (cl_env_copy->function=T3)->cfun.entry(3, v1_s_, v6_i_, T4);
   }
   T3 = _ecl_cdr(v10);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, T2, v2_cc_, T3);
  }
  if (!(T0==ECL_NIL)) { goto L67; }
  goto L68;
L69:;
L68:;
  goto L62;
L67:;
  goto L77;
L77:;
  v6_i_ = ecl_plus(v6_i_,ecl_make_fixnum(1));
  goto L61;
L62:;
  goto L49;
L49:;
  goto L39;
L40:;
  goto L38;
L38:;
  if (!(ecl_lowereq(v6_i_,v9_n_))) { goto L86; }
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[55];
   T0 = _ecl_car(v10);
   {
    cl_object v11;
    v11 = (v3_)->vector.self.t[21];
    T2 = _ecl_car(v11);
    {
     cl_object v12;
     v12 = (v3_)->vector.self.t[20];
     T4 = _ecl_car(v12);
     T5 = _ecl_cdr(v12);
     T3 = (cl_env_copy->function=T4)->cfun.entry(3, v6_i_, v9_n_, T5);
    }
    T4 = _ecl_cdr(v11);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, v1_s_, T3, T4);
   }
   T2 = _ecl_cdr(v10);
   v4_l_ = (cl_env_copy->function=T0)->cfun.entry(3, T1, v4_l_, T2);
  }
L86:;
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[56];
   T0 = _ecl_car(v10);
   T1 = _ecl_cdr(v10);
   value0 = (cl_env_copy->function=T0)->cfun.entry(2, v4_l_, T1);
   return value0;
  }
 }
}
/*      function definition for ISTRING;leftTrim;%Cc%;24              */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1088_istring_lefttrim__cc__24_(cl_object v1_s_, cl_object v2_cc_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  cl_object v5_i_;
  cl_object v6_n_;
  v4 = ECL_NIL;
  v5_i_ = ECL_NIL;
  v6_n_ = ecl_make_fixnum(0);
  {
   cl_object v7;
   v7 = (v3_)->vector.self.t[41];
   T0 = _ecl_car(v7);
   T1 = _ecl_cdr(v7);
   v6_n_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_s_, T1);
  }
  v5_i_ = (v3_)->vector.self.t[6];
  v4 = v6_n_;
L9:;
  if (ecl_greater(v5_i_,v4)) { goto L17; }
  {
   cl_object v7;
   v7 = (v3_)->vector.self.t[49];
   T1 = _ecl_car(v7);
   {
    cl_object v8;
    v8 = (v3_)->vector.self.t[52];
    T3 = _ecl_car(v8);
    T4 = _ecl_cdr(v8);
    T2 = (cl_env_copy->function=T3)->cfun.entry(3, v1_s_, v5_i_, T4);
   }
   T3 = _ecl_cdr(v7);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, T2, v2_cc_, T3);
  }
  if (!(T0==ECL_NIL)) { goto L15; }
  goto L16;
L17:;
L16:;
  goto L10;
L15:;
  goto L25;
L25:;
  v5_i_ = ecl_plus(v5_i_,ecl_make_fixnum(1));
  goto L9;
L10:;
  goto L8;
L8:;
  {
   cl_object v7;
   v7 = (v3_)->vector.self.t[21];
   T0 = _ecl_car(v7);
   {
    cl_object v8;
    v8 = (v3_)->vector.self.t[20];
    T2 = _ecl_car(v8);
    T3 = _ecl_cdr(v8);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, v5_i_, v6_n_, T3);
   }
   T2 = _ecl_cdr(v7);
   value0 = (cl_env_copy->function=T0)->cfun.entry(3, v1_s_, T1, T2);
   return value0;
  }
 }
}
/*      function definition for ISTRING;rightTrim;%Cc%;25             */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1089_istring_righttrim__cc__25_(cl_object v1_s_, cl_object v2_cc_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4, T5;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  cl_object v5_j_;
  v4 = ECL_NIL;
  v5_j_ = ECL_NIL;
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[41];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   v5_j_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_s_, T1);
  }
  v4 = (v3_)->vector.self.t[6];
L4:;
  if (ecl_lower(v5_j_,v4)) { goto L14; }
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[49];
   T1 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v3_)->vector.self.t[52];
    T3 = _ecl_car(v7);
    T4 = _ecl_cdr(v7);
    T2 = (cl_env_copy->function=T3)->cfun.entry(3, v1_s_, v5_j_, T4);
   }
   T3 = _ecl_cdr(v6);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, T2, v2_cc_, T3);
  }
  if (!(T0==ECL_NIL)) { goto L12; }
  goto L13;
L14:;
L13:;
  goto L5;
L12:;
  goto L22;
L22:;
  v5_j_ = ecl_plus(v5_j_,ecl_make_fixnum(-1));
  goto L4;
L5:;
  goto L3;
L3:;
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[21];
   T0 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v3_)->vector.self.t[20];
    T2 = _ecl_car(v7);
    {
     cl_object v8;
     v8 = (v3_)->vector.self.t[28];
     T4 = _ecl_car(v8);
     T5 = _ecl_cdr(v8);
     T3 = (cl_env_copy->function=T4)->cfun.entry(2, v1_s_, T5);
    }
    T4 = _ecl_cdr(v7);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, T3, v5_j_, T4);
   }
   T2 = _ecl_cdr(v6);
   value0 = (cl_env_copy->function=T0)->cfun.entry(3, v1_s_, T1, T2);
   return value0;
  }
 }
}
/*      function definition for ISTRING;concat;L%;26                  */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1090_istring_concat_l__26_(cl_object v1_l_, cl_object v2_)
{
 cl_object T0, T1, T2, T3, T4;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3_i_;
  cl_object v4;
  cl_object v5_s_;
  cl_object v6_t_;
  cl_object v7;
  cl_object v8;
  cl_object v9;
  cl_object v10;
  v3_i_ = ecl_make_fixnum(0);
  v4 = ECL_NIL;
  v5_s_ = ECL_NIL;
  v6_t_ = ECL_NIL;
  v7 = ECL_NIL;
  v8 = ecl_make_fixnum(0);
  v9 = ecl_make_fixnum(0);
  v10 = ECL_NIL;
  {
   cl_object v11;
   v11 = (v2_)->vector.self.t[9];
   T0 = _ecl_car(v11);
   v7 = ECL_NIL;
   v5_s_ = ECL_NIL;
   v10 = v1_l_;
L16:;
   if (ECL_ATOM(v10)) { goto L24; }
   v5_s_ = _ecl_car(v10);
   goto L22;
L24:;
   goto L17;
L22:;
   {
    cl_object v12;
    v12 = (v2_)->vector.self.t[13];
    T1 = _ecl_car(v12);
    T2 = _ecl_cdr(v12);
    v9 = (cl_env_copy->function=T1)->cfun.entry(2, v5_s_, T2);
   }
   if (Null(v7)) { goto L34; }
   v8 = ecl_plus(v8,v9);
   goto L28;
L34:;
   v8 = v9;
   v7 = ECL_T;
   goto L28;
L28:;
   v10 = _ecl_cdr(v10);
   goto L16;
L17:;
   goto L15;
L15:;
   if (Null(v7)) { goto L45; }
   T1 = v8;
   goto L44;
L45:;
   T1 = ecl_make_fixnum(0);
L44:;
   {
    cl_object v12;
    v12 = (v2_)->vector.self.t[42];
    T3 = _ecl_car(v12);
    T4 = _ecl_cdr(v12);
    T2 = (cl_env_copy->function=T3)->cfun.entry(1, T4);
   }
   T3 = _ecl_cdr(v11);
   v6_t_ = (cl_env_copy->function=T0)->cfun.entry(3, T1, T2, T3);
  }
  v3_i_ = (v2_)->vector.self.t[6];
  v5_s_ = ECL_NIL;
  v4 = v1_l_;
L53:;
  if (ECL_ATOM(v4)) { goto L61; }
  v5_s_ = _ecl_car(v4);
  goto L59;
L61:;
  goto L54;
L59:;
  {
   cl_object v11;
   v11 = (v2_)->vector.self.t[62];
   T0 = _ecl_car(v11);
   T1 = _ecl_cdr(v11);
   (cl_env_copy->function=T0)->cfun.entry(4, v6_t_, v5_s_, v3_i_, T1);
  }
  {
   cl_object v11;
   v11 = (v2_)->vector.self.t[13];
   T1 = _ecl_car(v11);
   T2 = _ecl_cdr(v11);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v5_s_, T2);
  }
  v3_i_ = ecl_plus(v3_i_,T0);
  goto L65;
L65:;
  v4 = _ecl_cdr(v4);
  goto L53;
L54:;
  goto L52;
L52:;
  value0 = v6_t_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for ISTRING;copyInto!;2%I%;27             */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1091_istring_copyinto__2_i__27_(cl_object v1_y_, cl_object v2_x_, cl_object v3_s_, cl_object v4_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5_n_;
  cl_object v6_m_;
  v5_n_ = ecl_make_fixnum(0);
  v6_m_ = ecl_make_fixnum(0);
  {
   cl_object v7;
   v7 = (v4_)->vector.self.t[13];
   T0 = _ecl_car(v7);
   T1 = _ecl_cdr(v7);
   v6_m_ = (cl_env_copy->function=T0)->cfun.entry(2, v2_x_, T1);
  }
  {
   cl_object v7;
   v7 = (v4_)->vector.self.t[13];
   T0 = _ecl_car(v7);
   T1 = _ecl_cdr(v7);
   v5_n_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_y_, T1);
  }
  T0 = (v4_)->vector.self.t[6];
  v3_s_ = ecl_minus(v3_s_,T0);
  if (ecl_lower(v3_s_,ecl_make_fixnum(0))) { goto L15; }
  T0 = ecl_plus(v3_s_,v6_m_);
  if (!(ecl_greater(T0,v5_n_))) { goto L13; }
  goto L14;
L15:;
L14:;
  value0 = ecl_function_dispatch(cl_env_copy,VV[75])(1, VV[18]) /*  error */;
  return value0;
L13:;
  ecl_function_dispatch(cl_env_copy,VV[91])(6, v1_y_, v3_s_, v6_m_, v2_x_, ecl_make_fixnum(0), v6_m_) /*  RPLACSTR */;
  value0 = v1_y_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for ISTRING;join;%L%;28                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1092_istring_join__l__28_(cl_object v1_sep_, cl_object v2_l_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6, T7;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_i_;
  cl_object v5_t_;
  cl_object v6;
  cl_object v7_s_;
  cl_object v8;
  cl_object v9;
  cl_object v10;
  cl_object v11;
  cl_object v12_lensep_;
  v4_i_ = ecl_make_fixnum(0);
  v5_t_ = ECL_NIL;
  v6 = ECL_NIL;
  v7_s_ = ECL_NIL;
  v8 = ECL_NIL;
  v9 = ecl_make_fixnum(0);
  v10 = ecl_make_fixnum(0);
  v11 = ECL_NIL;
  v12_lensep_ = ecl_make_fixnum(0);
  {
   cl_object v13;
   v13 = (v3_)->vector.self.t[64];
   T0 = _ecl_car(v13);
   T1 = _ecl_cdr(v13);
   if (Null((cl_env_copy->function=T0)->cfun.entry(2, v2_l_, T1))) { goto L11; }
  }
  {
   cl_object v13;
   v13 = (v3_)->vector.self.t[10];
   T0 = _ecl_car(v13);
   T1 = _ecl_cdr(v13);
   value0 = (cl_env_copy->function=T0)->cfun.entry(1, T1);
   return value0;
  }
L11:;
  {
   cl_object v14;
   v14 = (v3_)->vector.self.t[13];
   T0 = _ecl_car(v14);
   T1 = _ecl_cdr(v14);
   v12_lensep_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_sep_, T1);
  }
  {
   cl_object v14;
   v14 = (v3_)->vector.self.t[9];
   T0 = _ecl_car(v14);
   v8 = ECL_NIL;
   v7_s_ = ECL_NIL;
   v11 = v2_l_;
L28:;
   if (ECL_ATOM(v11)) { goto L36; }
   v7_s_ = _ecl_car(v11);
   goto L34;
L36:;
   goto L29;
L34:;
   {
    cl_object v15;
    v15 = (v3_)->vector.self.t[13];
    T1 = _ecl_car(v15);
    T2 = _ecl_cdr(v15);
    v10 = (cl_env_copy->function=T1)->cfun.entry(2, v7_s_, T2);
   }
   if (Null(v8)) { goto L46; }
   v9 = ecl_plus(v9,v10);
   goto L40;
L46:;
   v9 = v10;
   v8 = ECL_T;
   goto L40;
L40:;
   v11 = _ecl_cdr(v11);
   goto L28;
L29:;
   goto L27;
L27:;
   if (Null(v8)) { goto L57; }
   T1 = v9;
   goto L56;
L57:;
   T1 = ecl_make_fixnum(0);
L56:;
   {
    cl_object v15;
    v15 = (v3_)->vector.self.t[66];
    T3 = _ecl_car(v15);
    {
     cl_object v16;
     v16 = (v3_)->vector.self.t[65];
     T5 = _ecl_car(v16);
     T6 = _ecl_cdr(v16);
     T4 = (cl_env_copy->function=T5)->cfun.entry(2, v2_l_, T6);
    }
    T5 = _ecl_cdr(v15);
    T2 = (cl_env_copy->function=T3)->cfun.entry(2, T4, T5);
   }
   T3 = ecl_times(T2,v12_lensep_);
   T4 = ecl_plus(T1,T3);
   {
    cl_object v15;
    v15 = (v3_)->vector.self.t[42];
    T6 = _ecl_car(v15);
    T7 = _ecl_cdr(v15);
    T5 = (cl_env_copy->function=T6)->cfun.entry(1, T7);
   }
   T6 = _ecl_cdr(v14);
   v5_t_ = (cl_env_copy->function=T0)->cfun.entry(3, T4, T5, T6);
  }
  {
   cl_object v14;
   v14 = (v3_)->vector.self.t[62];
   T0 = _ecl_car(v14);
   {
    cl_object v15;
    v15 = (v3_)->vector.self.t[67];
    T2 = _ecl_car(v15);
    T3 = _ecl_cdr(v15);
    T1 = (cl_env_copy->function=T2)->cfun.entry(2, v2_l_, T3);
   }
   T2 = _ecl_cdr(v14);
   v5_t_ = (cl_env_copy->function=T0)->cfun.entry(4, v5_t_, T1, ecl_make_fixnum(1), T2);
  }
  {
   cl_object v14;
   v14 = (v3_)->vector.self.t[13];
   T1 = _ecl_car(v14);
   {
    cl_object v15;
    v15 = (v3_)->vector.self.t[67];
    T3 = _ecl_car(v15);
    T4 = _ecl_cdr(v15);
    T2 = (cl_env_copy->function=T3)->cfun.entry(2, v2_l_, T4);
   }
   T3 = _ecl_cdr(v14);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, T2, T3);
  }
  v4_i_ = ecl_plus(ecl_make_fixnum(1),T0);
  v7_s_ = ECL_NIL;
  {
   cl_object v14;
   v14 = (v3_)->vector.self.t[65];
   T0 = _ecl_car(v14);
   T1 = _ecl_cdr(v14);
   v6 = (cl_env_copy->function=T0)->cfun.entry(2, v2_l_, T1);
  }
L84:;
  if (ECL_ATOM(v6)) { goto L94; }
  v7_s_ = _ecl_car(v6);
  goto L92;
L94:;
  goto L85;
L92:;
  {
   cl_object v14;
   v14 = (v3_)->vector.self.t[62];
   T0 = _ecl_car(v14);
   T1 = _ecl_cdr(v14);
   v5_t_ = (cl_env_copy->function=T0)->cfun.entry(4, v5_t_, v1_sep_, v4_i_, T1);
  }
  v4_i_ = ecl_plus(v4_i_,v12_lensep_);
  {
   cl_object v14;
   v14 = (v3_)->vector.self.t[62];
   T0 = _ecl_car(v14);
   T1 = _ecl_cdr(v14);
   v5_t_ = (cl_env_copy->function=T0)->cfun.entry(4, v5_t_, v7_s_, v4_i_, T1);
  }
  {
   cl_object v14;
   v14 = (v3_)->vector.self.t[13];
   T1 = _ecl_car(v14);
   T2 = _ecl_cdr(v14);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v7_s_, T2);
  }
  v4_i_ = ecl_plus(v4_i_,T0);
  goto L98;
L98:;
  v6 = _ecl_cdr(v6);
  goto L84;
L85:;
  goto L83;
L83:;
  value0 = v5_t_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for ISTRING;qelt;%IC;29                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1093_istring_qelt__ic_29_(cl_object v1_s_, cl_object v2_i_, cl_object v3_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = (v3_)->vector.self.t[6];
 T1 = ecl_minus(v2_i_,T0);
 {
  ecl_character v4;
  v4 = ecl_char(v1_s_,ecl_fixnum(T1));
  value0 = ecl_make_fixnum(v4);
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for ISTRING;elt;%IC;30                    */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1094_istring_elt__ic_30_(cl_object v1_s_, cl_object v2_i_, cl_object v3_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = (v3_)->vector.self.t[6];
 if (ecl_lower(v2_i_,T0)) { goto L3; }
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[41];
  T1 = _ecl_car(v4);
  T2 = _ecl_cdr(v4);
  T0 = (cl_env_copy->function=T1)->cfun.entry(2, v1_s_, T2);
 }
 if (!(ecl_greater(v2_i_,T0))) { goto L1; }
 goto L2;
L3:;
L2:;
 value0 = ecl_function_dispatch(cl_env_copy,VV[75])(1, VV[18]) /*  error */;
 return value0;
L1:;
 T0 = (v3_)->vector.self.t[6];
 T1 = ecl_minus(v2_i_,T0);
 {
  ecl_character v4;
  v4 = ecl_char(v1_s_,ecl_fixnum(T1));
  value0 = ecl_make_fixnum(v4);
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for ISTRING;elt;%Us%;31                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1095_istring_elt__us__31_(cl_object v1_s_, cl_object v2_sg_, cl_object v3_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_h_;
  cl_object v5_l_;
  v4_h_ = ecl_make_fixnum(0);
  v5_l_ = ecl_make_fixnum(0);
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[38];
   T1 = _ecl_car(v6);
   T2 = _ecl_cdr(v6);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v2_sg_, T2);
  }
  T1 = (v3_)->vector.self.t[6];
  v5_l_ = ecl_minus(T0,T1);
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[39];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   if (Null((cl_env_copy->function=T0)->cfun.entry(2, v2_sg_, T1))) { goto L10; }
  }
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[40];
   T1 = _ecl_car(v6);
   T2 = _ecl_cdr(v6);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v2_sg_, T2);
  }
  T1 = (v3_)->vector.self.t[6];
  v4_h_ = ecl_minus(T0,T1);
  goto L9;
L10:;
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[41];
   T1 = _ecl_car(v6);
   T2 = _ecl_cdr(v6);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v1_s_, T2);
  }
  T1 = (v3_)->vector.self.t[6];
  v4_h_ = ecl_minus(T0,T1);
L9:;
  if (ecl_lower(v5_l_,ecl_make_fixnum(0))) { goto L22; }
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[13];
   T1 = _ecl_car(v6);
   T2 = _ecl_cdr(v6);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v1_s_, T2);
  }
  if (!(ecl_greatereq(v4_h_,T0))) { goto L20; }
  goto L21;
L22:;
L21:;
  value0 = ecl_function_dispatch(cl_env_copy,VV[75])(1, VV[24]) /*  error */;
  return value0;
L20:;
  T0 = ecl_minus(v4_h_,v5_l_);
  T1 = ecl_plus(T0,ecl_make_fixnum(1));
  T2 = ((ecl_float_nan_p(T1) || ecl_greatereq(ecl_make_fixnum(0),T1))?ecl_make_fixnum(0):T1);
  value0 = ecl_function_dispatch(cl_env_copy,VV[96])(3, v1_s_, v5_l_, T2) /*  SUBSTRING */;
  return value0;
 }
}
/*      function definition for ISTRING;hashUpdate!;Hs%Hs;32          */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1096_istring_hashupdate__hs_hs_32_(cl_object v1_hs_, cl_object v2_s_, cl_object v3_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = cl_sxhash(v2_s_);
 T1 = ecl_boole(ECL_BOOLXOR,(v1_hs_),(T0));
 T2 = ecl_times(ecl_make_fixnum(1099511628211),T1);
 value0 = ecl_boole(ECL_BOOLAND,(T2),(VV[40]));
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for ISTRING;match?;2%CB;33                */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1097_istring_match__2_cb_33_(cl_object v1_pattern_, cl_object v2_target_, cl_object v3_dontcare_, cl_object v4_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6, T7;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5_q_;
  cl_object v6;
  cl_object v7_p_;
  cl_object v8_i_;
  cl_object v9;
  cl_object v10;
  cl_object v11_s_;
  cl_object v12;
  cl_object v13;
  cl_object v14_m_;
  cl_object v15_n_;
  v5_q_ = ecl_make_fixnum(0);
  v6 = ECL_NIL;
  v7_p_ = ecl_make_fixnum(0);
  v8_i_ = ecl_make_fixnum(0);
  v9 = ECL_NIL;
  v10 = ECL_NIL;
  v11_s_ = ECL_NIL;
  v12 = ECL_NIL;
  v13 = ECL_NIL;
  v14_m_ = ecl_make_fixnum(0);
  v15_n_ = ecl_make_fixnum(0);
  {
   cl_object v16;
   v16 = (v4_)->vector.self.t[41];
   T0 = _ecl_car(v16);
   T1 = _ecl_cdr(v16);
   v15_n_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_pattern_, T1);
  }
  {
   cl_object v16;
   {
    cl_object v17;
    v17 = (v4_)->vector.self.t[48];
    T0 = _ecl_car(v17);
    {
     cl_object v18;
     v18 = (v4_)->vector.self.t[28];
     T1 = _ecl_car(v18);
     T2 = _ecl_cdr(v18);
     v14_m_ = (cl_env_copy->function=T1)->cfun.entry(2, v1_pattern_, T2);
    }
    T1 = _ecl_cdr(v17);
    v13 = (cl_env_copy->function=T0)->cfun.entry(4, v3_dontcare_, v1_pattern_, v14_m_, T1);
   }
   v16 = v13;
   {
    bool v17;
    v17 = ecl_greatereq(v13,ecl_make_fixnum(0));
    if (!(ecl_make_bool(v17)==ECL_NIL)) { goto L27; }
   }
   T0 = ecl_function_dispatch(cl_env_copy,VV[76])(3, v13, VV[19], VV[20]) /*  coerce_failure_msg */;
   ecl_function_dispatch(cl_env_copy,VV[75])(1, T0) /*  error         */;
L27:;
   v7_p_ = v16;
  }
  T0 = ecl_minus(v14_m_,ecl_make_fixnum(1));
  if (!(ecl_eql(v7_p_,T0))) { goto L30; }
  {
   cl_object v16;
   v16 = (v4_)->vector.self.t[14];
   T0 = _ecl_car(v16);
   T1 = _ecl_cdr(v16);
   value0 = (cl_env_copy->function=T0)->cfun.entry(3, v1_pattern_, v2_target_, T1);
   return value0;
  }
L30:;
  {
   cl_object v17;
   v17 = (v4_)->vector.self.t[72];
   T0 = _ecl_car(v17);
   T1 = _ecl_cdr(v17);
   if (Null((cl_env_copy->function=T0)->cfun.entry(3, v7_p_, v14_m_, T1))) { goto L34; }
  }
  {
   cl_object v17;
   v17 = (v4_)->vector.self.t[73];
   T1 = _ecl_car(v17);
   {
    cl_object v18;
    v18 = (v4_)->vector.self.t[21];
    T3 = _ecl_car(v18);
    {
     cl_object v19;
     v19 = (v4_)->vector.self.t[20];
     T5 = _ecl_car(v19);
     T6 = ecl_minus(v7_p_,ecl_make_fixnum(1));
     T7 = _ecl_cdr(v19);
     T4 = (cl_env_copy->function=T5)->cfun.entry(3, v14_m_, T6, T7);
    }
    T5 = _ecl_cdr(v18);
    T2 = (cl_env_copy->function=T3)->cfun.entry(3, v1_pattern_, T4, T5);
   }
   T3 = _ecl_cdr(v17);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, T2, v2_target_, T3);
  }
  if (!(T0==ECL_NIL)) { goto L34; }
  value0 = ECL_NIL;
  cl_env_copy->nvalues = 1;
  return value0;
L34:;
  v8_i_ = v7_p_;
  {
   cl_object v17;
   {
    cl_object v18;
    v18 = (v4_)->vector.self.t[48];
    T0 = _ecl_car(v18);
    T1 = ecl_plus(v7_p_,ecl_make_fixnum(1));
    T2 = _ecl_cdr(v18);
    v12 = (cl_env_copy->function=T0)->cfun.entry(4, v3_dontcare_, v1_pattern_, T1, T2);
   }
   v17 = v12;
   {
    bool v18;
    v18 = ecl_greatereq(v12,ecl_make_fixnum(0));
    if (!(ecl_make_bool(v18)==ECL_NIL)) { goto L56; }
   }
   T0 = ecl_function_dispatch(cl_env_copy,VV[76])(3, v12, VV[19], VV[20]) /*  coerce_failure_msg */;
   ecl_function_dispatch(cl_env_copy,VV[75])(1, T0) /*  error         */;
L56:;
   v5_q_ = v17;
  }
L59:;
  {
   cl_object v17;
   v17 = (v4_)->vector.self.t[72];
   T1 = _ecl_car(v17);
   T2 = ecl_minus(v14_m_,ecl_make_fixnum(1));
   T3 = _ecl_cdr(v17);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, v5_q_, T2, T3);
  }
  if (!(T0==ECL_NIL)) { goto L61; }
  goto L60;
L61:;
  {
   cl_object v17;
   v17 = (v4_)->vector.self.t[21];
   T0 = _ecl_car(v17);
   {
    cl_object v18;
    v18 = (v4_)->vector.self.t[20];
    T2 = _ecl_car(v18);
    T3 = ecl_plus(v7_p_,ecl_make_fixnum(1));
    T4 = ecl_minus(v5_q_,ecl_make_fixnum(1));
    T5 = _ecl_cdr(v18);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, T3, T4, T5);
   }
   T2 = _ecl_cdr(v17);
   v11_s_ = (cl_env_copy->function=T0)->cfun.entry(3, v1_pattern_, T1, T2);
  }
  {
   cl_object v17;
   {
    cl_object v18;
    v18 = (v4_)->vector.self.t[47];
    T0 = _ecl_car(v18);
    T1 = _ecl_cdr(v18);
    v10 = (cl_env_copy->function=T0)->cfun.entry(4, v11_s_, v2_target_, v8_i_, T1);
   }
   v17 = v10;
   {
    bool v18;
    v18 = ecl_greatereq(v10,ecl_make_fixnum(0));
    if (!(ecl_make_bool(v18)==ECL_NIL)) { goto L80; }
   }
   T0 = ecl_function_dispatch(cl_env_copy,VV[76])(3, v10, VV[19], VV[20]) /*  coerce_failure_msg */;
   ecl_function_dispatch(cl_env_copy,VV[75])(1, T0) /*  error         */;
L80:;
   v8_i_ = v17;
  }
  T0 = ecl_minus(v14_m_,ecl_make_fixnum(1));
  if (!(ecl_eql(v8_i_,T0))) { goto L83; }
  v9 = ECL_NIL;
  goto L12;
L83:;
  {
   cl_object v17;
   v17 = (v4_)->vector.self.t[13];
   T1 = _ecl_car(v17);
   T2 = _ecl_cdr(v17);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v11_s_, T2);
  }
  v8_i_ = ecl_plus(v8_i_,T0);
  v7_p_ = v5_q_;
  {
   cl_object v17;
   {
    cl_object v18;
    v18 = (v4_)->vector.self.t[48];
    T0 = _ecl_car(v18);
    T1 = ecl_plus(v5_q_,ecl_make_fixnum(1));
    T2 = _ecl_cdr(v18);
    v6 = (cl_env_copy->function=T0)->cfun.entry(4, v3_dontcare_, v1_pattern_, T1, T2);
   }
   v17 = v6;
   {
    bool v18;
    v18 = ecl_greatereq(v6,ecl_make_fixnum(0));
    if (!(ecl_make_bool(v18)==ECL_NIL)) { goto L100; }
   }
   T0 = ecl_function_dispatch(cl_env_copy,VV[76])(3, v6, VV[19], VV[20]) /*  coerce_failure_msg */;
   ecl_function_dispatch(cl_env_copy,VV[75])(1, T0) /*  error         */;
L100:;
   v5_q_ = v17;
  }
  goto L66;
L66:;
  goto L59;
L60:;
  goto L58;
L58:;
  {
   cl_object v17;
   v17 = (v4_)->vector.self.t[72];
   T0 = _ecl_car(v17);
   T1 = _ecl_cdr(v17);
   if (Null((cl_env_copy->function=T0)->cfun.entry(3, v7_p_, v15_n_, T1))) { goto L105; }
  }
  {
   cl_object v17;
   v17 = (v4_)->vector.self.t[51];
   T1 = _ecl_car(v17);
   {
    cl_object v18;
    v18 = (v4_)->vector.self.t[21];
    T3 = _ecl_car(v18);
    {
     cl_object v19;
     v19 = (v4_)->vector.self.t[20];
     T5 = _ecl_car(v19);
     T6 = ecl_plus(v7_p_,ecl_make_fixnum(1));
     T7 = _ecl_cdr(v19);
     T4 = (cl_env_copy->function=T5)->cfun.entry(3, T6, v15_n_, T7);
    }
    T5 = _ecl_cdr(v18);
    T2 = (cl_env_copy->function=T3)->cfun.entry(3, v1_pattern_, T4, T5);
   }
   T3 = _ecl_cdr(v17);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, T2, v2_target_, T3);
  }
  if (!(T0==ECL_NIL)) { goto L105; }
  value0 = ECL_NIL;
  cl_env_copy->nvalues = 1;
  return value0;
L105:;
  value0 = ECL_T;
  cl_env_copy->nvalues = 1;
  return value0;
L12:;
  value0 = v9;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for IndexedString;                        */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1098_indexedstring__(cl_object v1__1_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v2_pv__;
  cl_object v3;
  cl_object v4;
  cl_object v5;
  cl_object v6_;
  cl_object v7_dv__;
  cl_object v8dv_1;
  v2_pv__ = ECL_NIL;
  v3 = ECL_NIL;
  v4 = ECL_NIL;
  v5 = ECL_NIL;
  v6_ = ECL_NIL;
  v7_dv__ = ECL_NIL;
  v8dv_1 = ECL_NIL;
  v8dv_1 = v1__1_;
  v7_dv__ = cl_list(2, VV[43], v8dv_1);
  v6_ = ecl_function_dispatch(cl_env_copy,VV[100])(1, ecl_make_fixnum(86)) /*  GETREFV */;
  (v6_)->vector.self.t[0]= v7_dv__;
  T0 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  T1 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T0, VV[44]) /*  HasCategory */;
  T2 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  T3 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T2, VV[45]) /*  HasCategory */;
  T4 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  T5 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T4, VV[46]) /*  HasCategory */;
  T6 = ecl_function_dispatch(cl_env_copy,VV[103])(0) /*  Integer      */;
  T7 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T6, VV[44]) /*  HasCategory */;
  T8 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  T9 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T8, VV[47]) /*  HasCategory */;
  T10 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character   */;
  v5 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T10, VV[48]) /*  HasCategory */;
  value0 = v5;
  if ((value0)!=ECL_NIL) { goto L20; }
  T11 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character   */;
  T10 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T11, VV[44]) /*  HasCategory */;
  goto L18;
L20:;
  T10 = value0;
  goto L18;
L18:;
  T11 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character   */;
  v4 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T11, VV[49]) /*  HasCategory */;
  T12 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character   */;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, T12, VV[50]) /*  HasCategory */)) { goto L25; }
  T11 = v4;
  goto L23;
L25:;
  T11 = ECL_NIL;
  goto L23;
L23:;
  value0 = v5;
  if ((value0)!=ECL_NIL) { goto L29; }
  T13 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character   */;
  value0 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T13, VV[44]) /*  HasCategory */;
  if ((value0)!=ECL_NIL) { goto L29; }
  T12 = v4;
  goto L27;
L29:;
  T12 = value0;
  goto L27;
L27:;
  T14 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character   */;
  value0 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T14, VV[47]) /*  HasCategory */;
  if ((value0)!=ECL_NIL) { goto L34; }
  value0 = v5;
  if ((value0)!=ECL_NIL) { goto L34; }
  T14 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character   */;
  value0 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T14, VV[45]) /*  HasCategory */;
  if ((value0)!=ECL_NIL) { goto L34; }
  T14 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character   */;
  value0 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T14, VV[44]) /*  HasCategory */;
  if ((value0)!=ECL_NIL) { goto L34; }
  T13 = v4;
  goto L32;
L34:;
  T13 = value0;
  goto L32;
L32:;
  T14 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character   */;
  v3 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T14, VV[51]) /*  HasCategory */;
  value0 = v3;
  if ((value0)!=ECL_NIL) { goto L42; }
  value0 = v5;
  if ((value0)!=ECL_NIL) { goto L42; }
  T15 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character   */;
  value0 = ecl_function_dispatch(cl_env_copy,VV[102])(2, T15, VV[44]) /*  HasCategory */;
  if ((value0)!=ECL_NIL) { goto L42; }
  T14 = v4;
  goto L40;
L42:;
  T14 = value0;
  goto L40;
L40:;
  T15 = cl_list(13, T1, T3, T5, T7, T9, v5, T10, v4, T11, T12, T13, v3, T14);
  v2_pv__ = ecl_function_dispatch(cl_env_copy,VV[104])(3, ecl_make_fixnum(0), ecl_make_fixnum(0), T15) /*  buildPredVector */;
  (v6_)->vector.self.t[3]= v2_pv__;
  T0 = ecl_list1(v8dv_1);
  T1 = CONS(ecl_make_fixnum(1),v6_);
  ecl_function_dispatch(cl_env_copy,VV[105])(4, ECL_SYM_VAL(cl_env_copy,VV[52]), VV[43], T0, T1) /*  haddProp */;
  ecl_function_dispatch(cl_env_copy,VV[106])(1, v6_) /*  stuffDomainSlots */;
  (v6_)->vector.self.t[6]= v1__1_;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[53]) /*  HasCategory */)) { goto L51; }
  ecl_function_dispatch(cl_env_copy,VV[107])(2, v6_, ecl_make_fixnum(8192)) /*  augmentPredVector */;
  goto L49;
L51:;
  goto L49;
L49:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L55; }
  ecl_function_dispatch(cl_env_copy,VV[107])(2, v6_, ecl_make_fixnum(16384)) /*  augmentPredVector */;
  goto L53;
L55:;
  goto L53;
L53:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L59; }
  T0 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, T0, VV[47]) /*  HasCategory */)) { goto L59; }
  ecl_function_dispatch(cl_env_copy,VV[107])(2, v6_, ecl_make_fixnum(32768)) /*  augmentPredVector */;
  goto L57;
L59:;
  goto L57;
L57:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L64; }
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[53]) /*  HasCategory */)) { goto L64; }
  ecl_function_dispatch(cl_env_copy,VV[107])(2, v6_, ecl_make_fixnum(65536)) /*  augmentPredVector */;
  goto L62;
L64:;
  goto L62;
L62:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L69; }
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[53]) /*  HasCategory */)) { goto L69; }
  T0 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, T0, VV[44]) /*  HasCategory */)) { goto L69; }
  ecl_function_dispatch(cl_env_copy,VV[107])(2, v6_, ecl_make_fixnum(131072)) /*  augmentPredVector */;
  goto L67;
L69:;
  goto L67;
L67:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L75; }
  T0 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, T0, VV[44]) /*  HasCategory */)) { goto L75; }
  ecl_function_dispatch(cl_env_copy,VV[107])(2, v6_, ecl_make_fixnum(262144)) /*  augmentPredVector */;
  goto L73;
L75:;
  goto L73;
L73:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L85; }
  if ((v5)!=ECL_NIL) { goto L82; }
  goto L83;
L85:;
  goto L83;
L83:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L80; }
  T0 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, T0, VV[44]) /*  HasCategory */)) { goto L80; }
  goto L81;
L82:;
L81:;
  ecl_function_dispatch(cl_env_copy,VV[107])(2, v6_, ecl_make_fixnum(524288)) /*  augmentPredVector */;
  goto L78;
L80:;
  goto L78;
L78:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L95; }
  if ((v5)!=ECL_NIL) { goto L92; }
  goto L93;
L95:;
  goto L93;
L93:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L99; }
  T0 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  if ((ecl_function_dispatch(cl_env_copy,VV[102])(2, T0, VV[44]) /*  HasCategory */)!=ECL_NIL) { goto L92; }
  goto L97;
L99:;
  goto L97;
L97:;
  if (Null(v4)) { goto L90; }
  goto L91;
L92:;
L91:;
  ecl_function_dispatch(cl_env_copy,VV[107])(2, v6_, ecl_make_fixnum(1048576)) /*  augmentPredVector */;
  goto L88;
L90:;
  goto L88;
L88:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L108; }
  if ((v5)!=ECL_NIL) { goto L105; }
  goto L106;
L108:;
  goto L106;
L106:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L112; }
  T0 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  if ((ecl_function_dispatch(cl_env_copy,VV[102])(2, T0, VV[44]) /*  HasCategory */)!=ECL_NIL) { goto L105; }
  goto L110;
L112:;
  goto L110;
L110:;
  if (Null(v3)) { goto L103; }
  goto L104;
L105:;
L104:;
  ecl_function_dispatch(cl_env_copy,VV[107])(2, v6_, ecl_make_fixnum(2097152)) /*  augmentPredVector */;
  goto L101;
L103:;
  goto L101;
L101:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L116; }
  T0 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, T0, VV[45]) /*  HasCategory */)) { goto L116; }
  ecl_function_dispatch(cl_env_copy,VV[107])(2, v6_, ecl_make_fixnum(4194304)) /*  augmentPredVector */;
  goto L114;
L116:;
  goto L114;
L114:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L126; }
  T0 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  if ((ecl_function_dispatch(cl_env_copy,VV[102])(2, T0, VV[47]) /*  HasCategory */)!=ECL_NIL) { goto L123; }
  goto L124;
L126:;
  goto L124;
L124:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L130; }
  if ((v5)!=ECL_NIL) { goto L123; }
  goto L128;
L130:;
  goto L128;
L128:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L134; }
  T0 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  if ((ecl_function_dispatch(cl_env_copy,VV[102])(2, T0, VV[45]) /*  HasCategory */)!=ECL_NIL) { goto L123; }
  goto L132;
L134:;
  goto L132;
L132:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[102])(2, v6_, VV[54]) /*  HasCategory */)) { goto L138; }
  T0 = ecl_function_dispatch(cl_env_copy,VV[101])(0) /*  Character    */;
  if ((ecl_function_dispatch(cl_env_copy,VV[102])(2, T0, VV[44]) /*  HasCategory */)!=ECL_NIL) { goto L123; }
  goto L136;
L138:;
  goto L136;
L136:;
  if (Null(v4)) { goto L121; }
  goto L122;
L123:;
L122:;
  ecl_function_dispatch(cl_env_copy,VV[107])(2, v6_, ecl_make_fixnum(8388608)) /*  augmentPredVector */;
  goto L119;
L121:;
  goto L119;
L119:;
  v2_pv__ = (v6_)->vector.self.t[3];
  value0 = v6_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for IndexedString                         */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L1099_indexedstring_(cl_object volatile v1)
{
 cl_object T0, T1;
 cl_object volatile env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object volatile value0;
TTL:
 {
  volatile cl_object v2;
  v2 = ECL_NIL;
  T0 = ecl_list1(v1);
  T1 = ecl_gethash_safe(VV[43],ECL_SYM_VAL(cl_env_copy,VV[52]),ECL_NIL);
  v2 = ecl_function_dispatch(cl_env_copy,VV[109])(3, T0, T1, VV[55]) /*  lassocShiftWithFunction */;
  if (Null(v2)) { goto L3; }
  value0 = ecl_function_dispatch(cl_env_copy,VV[110])(1, v2) /*  CDRwithIncrement */;
  return value0;
L3:;
  {
   volatile bool unwinding = FALSE;
   cl_index v3=ECL_STACK_INDEX(cl_env_copy),v4;
   ecl_frame_ptr next_fr;
   ecl_frs_push(cl_env_copy,ECL_PROTECT_TAG);
   if (__ecl_frs_push_result) {
     unwinding = TRUE; next_fr=cl_env_copy->nlj_fr;
   } else {
   {
    cl_object v5;
    v5 = ecl_function_dispatch(cl_env_copy,VV[42])(1, v1) /*  IndexedString; */;
    v2 = ECL_T;
    cl_env_copy->values[0] = v5;
    cl_env_copy->nvalues = 1;
   }
   }
   ecl_frs_pop(cl_env_copy);
   v4=ecl_stack_push_values(cl_env_copy);
   if ((v2)!=ECL_NIL) { goto L10; }
   cl_remhash(VV[43], ECL_SYM_VAL(cl_env_copy,VV[52]));
L10:;
   ecl_stack_pop_values(cl_env_copy,v4);
   if (unwinding) ecl_unwind(cl_env_copy,next_fr);
   ECL_STACK_SET_INDEX(cl_env_copy,v3);
   return cl_env_copy->values[0];
  }
 }
}

#include "/Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/_build/target/aarch64-apple-darwin23.6.0/algebra/ISTRING.data"
#ifdef __cplusplus
extern "C"
#endif
ECL_DLLEXPORT void init_fas_CODE(cl_object flag)
{
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
 cl_object *VVtemp;
 if (flag != OBJNULL){
 Cblock = flag;
 #ifndef ECL_DYNAMIC_VV
 flag->cblock.data = VV;
 #endif
 flag->cblock.data_size = VM;
 flag->cblock.temp_data_size = VMtemp;
 flag->cblock.data_text = compiler_data_text;
 flag->cblock.cfuns_size = compiler_cfuns_size;
 flag->cblock.cfuns = compiler_cfuns;
 flag->cblock.source = ecl_make_constant_base_string("/Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/pre-generated/src/algebra/ISTRING.lsp",-1);
 return;}
 #ifdef ECL_DYNAMIC_VV
 VV = Cblock->cblock.data;
 #endif
 Cblock->cblock.data_text = (const cl_object *)"@EcLtAg:init_fas_CODE@";
 VVtemp = Cblock->cblock.temp_data;
 ECL_DEFINE_SETF_FUNCTIONS
  ecl_function_dispatch(cl_env_copy,VV[58])(3, VV[0], VV[1], VV[2]) /*  PUT */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[0], ECL_SYM("LOCATION",1862), VVtemp[0], VVtemp[1]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[0], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[2]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[59]);                          /*  ISTRING;new;NniC%;1 */
  ecl_function_dispatch(cl_env_copy,VV[58])(3, VV[3], VV[1], VVtemp[3]) /*  PUT */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[3], ECL_SYM("LOCATION",1862), VVtemp[4], VVtemp[5]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[3], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[6]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[60]);                          /*  ISTRING;empty;%;2 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[4], ECL_SYM("LOCATION",1862), VVtemp[7], VVtemp[8]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[4], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[9]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[62]);                          /*  ISTRING;empty?;%B;3 */
  ecl_function_dispatch(cl_env_copy,VV[58])(3, VV[5], VV[1], VV[6]) /*  PUT */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[5], ECL_SYM("LOCATION",1862), VVtemp[10], VVtemp[11]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[5], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[9]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[63]);                          /*  ISTRING;#;%Nni;4 */
  ecl_function_dispatch(cl_env_copy,VV[58])(3, VV[7], VV[1], ECL_SYM("EQUAL",337)) /*  PUT */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[7], ECL_SYM("LOCATION",1862), VVtemp[12], VVtemp[13]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[7], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[14]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[64]);                          /*  ISTRING;=;2%B;5 */
  ecl_function_dispatch(cl_env_copy,VV[58])(3, VV[8], VV[1], VVtemp[15]) /*  PUT */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[8], ECL_SYM("LOCATION",1862), VVtemp[16], VVtemp[17]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[8], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[14]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[65]);                          /*  ISTRING;<;2%B;6 */
  ecl_function_dispatch(cl_env_copy,VV[58])(3, VV[9], VV[1], VV[10]) /*  PUT */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[9], ECL_SYM("LOCATION",1862), VVtemp[18], VVtemp[19]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[9], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[14]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[67]);                          /*  ISTRING;concat;3%;7 */
  ecl_function_dispatch(cl_env_copy,VV[58])(3, VV[11], VV[1], ECL_SYM("COPY-SEQ",262)) /*  PUT */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[11], ECL_SYM("LOCATION",1862), VVtemp[20], VVtemp[21]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[11], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[9]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[68]);                          /*  ISTRING;copy;2%;8 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[12], ECL_SYM("LOCATION",1862), VVtemp[22], VVtemp[23]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[12], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[24]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[69]);                          /*  ISTRING;insert;2%I%;9 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[13], ECL_SYM("LOCATION",1862), VVtemp[25], VVtemp[26]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[13], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[9]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[70]);                          /*  ISTRING;coerce;%Of;10 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[14], ECL_SYM("LOCATION",1862), VVtemp[27], VVtemp[28]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[14], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[9]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[71]);                          /*  ISTRING;minIndex;%I;11 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[15], ECL_SYM("LOCATION",1862), VVtemp[29], VVtemp[30]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[15], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[9]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[72]);                          /*  ISTRING;upperCase!;2%;12 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[16], ECL_SYM("LOCATION",1862), VVtemp[31], VVtemp[32]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[16], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[9]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[73]);                          /*  ISTRING;lowerCase!;2%;13 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[17], ECL_SYM("LOCATION",1862), VVtemp[33], VVtemp[34]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[17], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[35]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[74]);                          /*  ISTRING;replace;%Us2%;14 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[21], ECL_SYM("LOCATION",1862), VVtemp[36], VVtemp[37]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[21], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[38]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[77]);                          /*  ISTRING;qsetelt!;%I2C;15 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[22], ECL_SYM("LOCATION",1862), VVtemp[39], VVtemp[40]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[22], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[38]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[78]);                          /*  ISTRING;setelt!;%I2C;16 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[23], ECL_SYM("LOCATION",1862), VVtemp[41], VVtemp[42]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[23], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[43]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[79]);                          /*  ISTRING;substring?;2%IB;17 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[25], ECL_SYM("LOCATION",1862), VVtemp[44], VVtemp[45]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[25], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[46]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[80]);                          /*  ISTRING;position;2%2I;18 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[26], ECL_SYM("LOCATION",1862), VVtemp[47], VVtemp[48]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[26], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[49]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[82]);                          /*  ISTRING;position;C%2I;19 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[27], ECL_SYM("LOCATION",1862), VVtemp[50], VVtemp[51]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[27], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[52]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[83]);                          /*  ISTRING;position;Cc%2I;20 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[28], ECL_SYM("LOCATION",1862), VVtemp[53], VVtemp[54]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[28], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[14]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[84]);                          /*  ISTRING;suffix?;2%B;21 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[29], ECL_SYM("LOCATION",1862), VVtemp[55], VVtemp[56]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[29], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[57]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[85]);                          /*  ISTRING;split;%CL;22 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[30], ECL_SYM("LOCATION",1862), VVtemp[58], VVtemp[59]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[30], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[60]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[86]);                          /*  ISTRING;split;%CcL;23 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[31], ECL_SYM("LOCATION",1862), VVtemp[61], VVtemp[62]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[31], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[60]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[87]);                          /*  ISTRING;leftTrim;%Cc%;24 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[32], ECL_SYM("LOCATION",1862), VVtemp[63], VVtemp[64]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[32], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[60]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[88]);                          /*  ISTRING;rightTrim;%Cc%;25 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[33], ECL_SYM("LOCATION",1862), VVtemp[65], VVtemp[66]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[33], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[67]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[89]);                          /*  ISTRING;concat;L%;26 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[34], ECL_SYM("LOCATION",1862), VVtemp[68], VVtemp[69]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[34], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[70]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[90]);                          /*  ISTRING;copyInto!;2%I%;27 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[35], ECL_SYM("LOCATION",1862), VVtemp[71], VVtemp[72]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[35], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[73]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[92]);                          /*  ISTRING;join;%L%;28 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[36], ECL_SYM("LOCATION",1862), VVtemp[74], VVtemp[75]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[36], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[76]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[93]);                          /*  ISTRING;qelt;%IC;29 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[37], ECL_SYM("LOCATION",1862), VVtemp[77], VVtemp[78]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[37], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[76]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[94]);                          /*  ISTRING;elt;%IC;30 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[38], ECL_SYM("LOCATION",1862), VVtemp[79], VVtemp[80]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[38], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[81]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[95]);                          /*  ISTRING;elt;%Us%;31 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[39], ECL_SYM("LOCATION",1862), VVtemp[82], VVtemp[83]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[39], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[84]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[97]);                          /*  ISTRING;hashUpdate!;Hs%Hs;32 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[41], ECL_SYM("LOCATION",1862), VVtemp[85], VVtemp[86]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[41], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[87]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[98]);                          /*  ISTRING;match?;2%CB;33 */
  (cl_env_copy->function=(ECL_SYM("MAPC",545)->symbol.gfdef))->cfun.entry(2, ECL_SYM("PROCLAIM",668), VVtemp[88]) /*  MAPC */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[42], ECL_SYM("LOCATION",1862), VVtemp[89], VVtemp[90]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[42], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[91]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[99]);                          /*  IndexedString;  */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[43], ECL_SYM("LOCATION",1862), VVtemp[92], VVtemp[93]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[43], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[94]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[108]);                         /*  IndexedString   */
 {
  cl_object T0, T1, T2, T3;
  cl_object volatile env0 = ECL_NIL;
  T0 = ecl_function_dispatch(cl_env_copy,VV[111])(2, ecl_make_fixnum(13), VVtemp[97]) /*  makeByteWordVec2 */;
  T1 = ecl_function_dispatch(cl_env_copy,VV[111])(2, ecl_make_fixnum(85), VVtemp[100]) /*  makeByteWordVec2 */;
  T2 = cl_listX(4, T0, VVtemp[98], VVtemp[99], T1);
  T3 = cl_list(5, VVtemp[95], VVtemp[96], ECL_NIL, T2, VV[57]);
  ecl_function_dispatch(cl_env_copy,VV[112])(3, VV[43], VV[56], T3) /*  MAKEPROP */;
 }
}
