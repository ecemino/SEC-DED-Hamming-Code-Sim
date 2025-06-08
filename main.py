import tkinter as tk
from tkinter import messagebox
import random

def is_power_of_two(x):
    return x > 0 and (x & (x - 1)) == 0


def calculate_hamming_secded(data_bits):
    m = len(data_bits)

    k = 0  # check bit sayısı
    while 2 ** k < m+k +1:
        k += 1

    total_length = m + k
    hamming = [' ' for _ in range(total_length)]

    abstract_indexes = list(range(1, total_length + 1))[::-1]  # hamming kod hesaplamaları için soyut bir indeks listesi
                                                               # 1'den başlayarak sağ baştan sayar

    data_index = 0

    # asıl veri işlenir
    for i in range(total_length):
        if not is_power_of_two(abstract_indexes[i]):
            hamming[i] = data_bits[data_index]
            data_index += 1

    # kontrol bitleri hesaplanır
    xor_sum = 0
    for i in range(total_length):
        if hamming[i] == '1':
            xor_sum ^= abstract_indexes[i]
    check_bits_str = format(xor_sum, f'0{k}b')

    # kontrol bitleri işlenir
    check_index = 0
    for i in range(total_length):
        if is_power_of_two(abstract_indexes[i]):
            hamming[i] = check_bits_str[check_index]
            check_index += 1

    total_ones = hamming.count('1')
    sec_ded_bit = str(total_ones % 2)  # parity bit hesabı

    final_code = sec_ded_bit + ''.join(hamming)
    return final_code


def introduce_error(code, position):
    # position soyut konumu ifade eder (n - 1)
    if position <= 0 or position > len(code):
        raise ValueError("Hata pozisyonu kod uzunluğundan büyük veya negatif olamaz.")
    bit_pos = len(code) - position  # string içindeki asıl indeksi

    code_list = list(code)
    code_list[bit_pos] = '1' if code_list[bit_pos] == '0' else '0'
    return ''.join(code_list)


def decode_and_correct(received_code):

    # parity biti en başta
    parity_bit = int(received_code[0])
    code = list(received_code)
    n = len(code)

    # Soyut indeksler
    abstract_indexes = list(range(1, n + 1))[::-1]
    check_bits_str = ""
    data_1s_sum = 0

    # 2'nin kuvveti olan soyut indekslerden check bitlerini alır
    for i in range(1, n):
        if is_power_of_two(abstract_indexes[i]):  # 2'nin kuvvetiyse check biti
            check_bits_str += str(code[i])

        elif code[i] == '1':
            print(abstract_indexes[i])
            data_1s_sum ^= abstract_indexes[i]

    print(check_bits_str)
    check_bin = int(check_bits_str, 2)  # bu noktada check bitleri birleştirilerek binary int hale getirilmiştir

    syndrome = check_bin ^ data_1s_sum  # hata biti abstract int

    error_index = n - syndrome  # hatalı bitin asıl indeksi

    # olması beklenen parity biti hesaplanır
    total_ones = received_code[1:].count('1')
    expected_sec_ded = total_ones % 2  # 0: hata yok veya çift hata, 1: tek hata


    # Hata türünü belirlenir
    if syndrome == 0 and parity_bit == expected_sec_ded:
        error_type = "No error detected."
    elif syndrome != 0 and parity_bit == expected_sec_ded:
        error_type = "Double-bit error detected (cannot correct)."
    elif syndrome != 0 and parity_bit != expected_sec_ded:
        error_type = f"Single-bit error detected at bit no. {syndrome}"
    else:
        error_type = "Error detected but unable to classify."

    # single-bit error ise düzeltilir
    if error_type.startswith("Single-bit error"):

        # hatalı biti düzelt
        if 0 <= error_index < n:
            code[error_index] = '1' if code[error_index] == '0' else '0'
        else:
            error_type += "error position out of range!"

    corrected_code = ''.join(code)

    return {
        "error_type": error_type,
        "error_position_abstract_index": syndrome,
        "corrected_code": corrected_code
    }

memory = []

def is_valid_binary(data):
    return data.isdigit() and set(data).issubset({'0', '1'}) and len(data) in {8, 16, 32}

def generate_hamming():
    data = input_entry.get()

    if not is_valid_binary(data):
        messagebox.showerror("Invalid Input", "Please enter a binary value of 8, 16, or 32 bits.")
        return

    code = calculate_hamming_secded(data)
    memory.append(code)
    update_memory_display()
    input_entry.delete(0, tk.END)


def update_memory_display():
    output_text.delete(1.0, tk.END)

    # bellek içeiriğini yazdırır
    for i, code in enumerate(memory):
        output_text.insert(tk.END, f"[{i}] {code}\n")


def read_and_corrupt():
    try:
        index = int(memory_index_entry.get())
        if not (0 <= index < len(memory)):
            raise IndexError

        code = memory[index]
        corrupted = code

        # bozulma konumları validse bozar yoksa error mesajı verir
        corruption_pos_input = error_entry.get().strip()

        if corruption_pos_input:
            try:
                custom_positions = [int(pos.strip()) for pos in corruption_pos_input.split(",")]

                for pos in custom_positions:
                    if not (1 <= pos <= len(code)):
                        raise ValueError(f"Position {pos} is out of bounds.")

                for pos in custom_positions:
                    corrupted = introduce_error(corrupted, pos)

            except Exception as e:
                messagebox.showerror("Error", f"Invalid custom positions: {e}")
                return
        else:
            # istenen bozulma konumu girilmezse random bozar
            bit_positions = random.sample(range(1, len(code)+1), error_var.get())
            for pos in bit_positions:
                corrupted = introduce_error(corrupted, pos)

        result = decode_and_correct(corrupted)

        output_text.insert(tk.END, "-"*51 + "\n")
        output_text.insert(tk.END, f"Original Code:  {memory[index]}\n")
        output_text.insert(tk.END, f"Corrupted Code: {corrupted}\n")
        output_text.insert(tk.END, f"Error Type: {result['error_type']}\n")
        output_text.insert(tk.END, f"Updated Code:   {result['corrected_code']}\n")
        output_text.insert(tk.END, "-"*51 + "\n")

    except (ValueError, IndexError):
        messagebox.showerror("Error", "Invalid memory index.")

# GUI penceresi

root = tk.Tk()
root.title("Hamming SEC-DED Simulator")
root.geometry("800x600")

tk.Label(root, text="Enter 8/16/32-bit Binary Data:").pack()
input_entry = tk.Entry(root, width=50)
input_entry.pack()

gen_button = tk.Button(root, text="Save to Memory", command=generate_hamming)
gen_button.pack(pady=5)

# okunacak memory şndeksi girme bloğu
tk.Label(root, text="\nSelect Memory Index:").pack()
memory_index_entry = tk.Entry(root, width=5)
memory_index_entry.pack()
memory_index_entry.insert(0, "0")

# bozulacak bit konumlarını girme bloğu (rastgele bozulma için boş bırakılabilir)
tk.Label(root, text="\n(optional) Error Bits to Corrupt:").pack()
error_entry = tk.Entry(root, width=20)
error_entry.pack()
tk.Label(root, text="(indexed as n, n-1, ... , 2, 1)\n1 or 2 entries only: i.e. [3] or [4,6]\n\n").pack()

error_frame = tk.Frame(root)
error_frame.pack()

tk.Label(error_frame, text="Number of errors to introduce:").pack(side=tk.LEFT)  # single ya da double-bit bozulma seçimi
error_var = tk.IntVar(value=1)
tk.Spinbox(error_frame, from_=1, to=2, width=3, textvariable=error_var).pack(side=tk.LEFT)

read_button = tk.Button(root, text="Read from Memory and Introduce Error(s)", command=read_and_corrupt)
read_button.pack(pady=5)

output_text = tk.Text(root, height=25, width=100)
output_text.pack(pady=10)

root.mainloop()
