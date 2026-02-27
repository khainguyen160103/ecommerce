import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { UserService } from "@/requests/users";
import toast from 'react-hot-toast';

export const useUsers = (userId?: string, options?: { enableGetAll?: boolean }) => { 
    const queryClient = useQueryClient();
    const { enableGetAll = true } = options || {};
    
    const usersData = useQuery({ 
        queryKey: ['users'],
        queryFn: () => UserService.getAll(),
        enabled: enableGetAll
    });

    const userIdData = useQuery({ 
        queryKey: ['user', userId], 
        queryFn: () => UserService.getById(userId ? userId : ''),
        enabled: !!userId
    });

    const createMutation = useMutation({ 
        mutationFn: (data: any) => UserService.create(data),
        onSuccess: () => {
            toast.success('Tạo người dùng thành công');
            queryClient.invalidateQueries({ queryKey: ['users'] });
        },
        onError: () => {
            toast.error('Lỗi tạo người dùng');
        }
    });

    const updateMutation = useMutation({ 
        mutationFn: ({ id, data }: { id: string; data: any }) => 
            UserService.update(id, data),
        onSuccess: () => {
            toast.success('Cập nhật người dùng thành công');
            queryClient.invalidateQueries({ queryKey: ['users'] });
        },
        onError: () => {
            toast.error('Lỗi cập nhật người dùng');
        }
    });

    const deleteMutation = useMutation({ 
        mutationFn: (id: string) => UserService.delete(id),
        onSuccess: () => {
            toast.success('Xóa người dùng thành công');
            queryClient.invalidateQueries({ queryKey: ['users'] });
        },
        onError: () => {
            toast.error('Lỗi xóa người dùng');
        }
    });
    
    return { 
        usersData, 
        userIdData,
        createMutation,
        updateMutation,
        deleteMutation
    };
}